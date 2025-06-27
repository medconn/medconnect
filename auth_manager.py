#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de autenticación para MedConnect
Maneja registro, login y gestión de sesiones con Google Sheets
"""

import gspread
from google.oauth2.service_account import Credentials
import json
import bcrypt
from datetime import datetime
import uuid
import re
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración
GOOGLE_SHEETS_ID = "1UvnO2lpZSyv13Hf2eG--kQcTff5BBh7jrZ6taFLJypU"

# Cargar credenciales
credentials_file = os.environ.get('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
with open(credentials_file, 'r') as f:
    GOOGLE_CREDS = json.load(f)

class AuthManager:
    def __init__(self):
        """Inicializar el gestor de autenticación"""
        try:
            # Conectar con Google Sheets
            credentials = Credentials.from_service_account_info(
                GOOGLE_CREDS, 
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            self.gc = gspread.authorize(credentials)
            self.spreadsheet = self.gc.open_by_key(GOOGLE_SHEETS_ID)
            
            # Obtener hoja de usuarios
            try:
                self.users_sheet = self.spreadsheet.worksheet('Usuarios')
            except gspread.exceptions.WorksheetNotFound:
                logger.error("❌ Hoja 'Usuarios' no encontrada. Ejecuta setup_auth_sheets.py primero.")
                raise Exception("Hoja de usuarios no configurada")
                
            logger.info("✅ AuthManager inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando AuthManager: {e}")
            raise

    def validate_email(self, email):
        """Validar formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_password(self, password):
        """Validar fortaleza de contraseña"""
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        if not re.search(r'[A-Za-z]', password):
            return False, "La contraseña debe contener al menos una letra"
        if not re.search(r'[0-9]', password):
            return False, "La contraseña debe contener al menos un número"
        return True, "Contraseña válida"

    def hash_password(self, password):
        """Crear hash de contraseña"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password, hashed):
        """Verificar contraseña contra hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def email_exists(self, email):
        """Verificar si el email ya está registrado"""
        try:
            all_records = self.users_sheet.get_all_records()
            for record in all_records:
                if record.get('email', '').lower() == email.lower():
                    return True
            return False
        except Exception as e:
            logger.error(f"Error verificando email: {e}")
            return True  # En caso de error, asumir que existe para evitar duplicados

    def get_next_user_id(self):
        """Obtener el siguiente ID de usuario"""
        try:
            all_records = self.users_sheet.get_all_records()
            if not all_records:
                return 1
            max_id = max([int(record.get('id', 0)) for record in all_records])
            return max_id + 1
        except Exception as e:
            logger.error(f"Error obteniendo siguiente ID: {e}")
            return 1

    def register_user(self, user_data):
        """
        Registrar nuevo usuario
        user_data debe contener: email, password, nombre, apellido, telefono, 
        fecha_nacimiento, genero, direccion, ciudad, tipo_usuario
        """
        try:
            # Validaciones
            if not self.validate_email(user_data['email']):
                return False, "Formato de email inválido"
            
            if self.email_exists(user_data['email']):
                return False, "El email ya está registrado"
            
            is_valid, msg = self.validate_password(user_data['password'])
            if not is_valid:
                return False, msg
            
            # Campos requeridos
            required_fields = ['email', 'password', 'nombre', 'apellido', 'tipo_usuario']
            for field in required_fields:
                if not user_data.get(field):
                    return False, f"El campo {field} es requerido"
            
            # Preparar datos del usuario
            user_id = self.get_next_user_id()
            password_hash = self.hash_password(user_data['password'])
            current_time = datetime.now().isoformat()
            
            row_data = [
                user_id,
                user_data['email'].lower(),
                password_hash,
                user_data['nombre'],
                user_data['apellido'],
                user_data.get('telefono', ''),
                user_data.get('fecha_nacimiento', ''),
                user_data.get('genero', ''),
                user_data.get('direccion', ''),
                user_data.get('ciudad', ''),
                current_time,  # fecha_registro
                '',  # ultimo_acceso
                'activo',  # estado
                user_data['tipo_usuario'],  # tipo_usuario (paciente/profesional)
                'false'  # verificado
            ]
            
            # Agregar usuario a la hoja
            self.users_sheet.append_row(row_data)
            
            logger.info(f"✅ Usuario registrado: {user_data['email']}")
            return True, "Usuario registrado exitosamente"
            
        except Exception as e:
            logger.error(f"❌ Error registrando usuario: {e}")
            return False, "Error interno del servidor"

    def login_user(self, email, password):
        """
        Iniciar sesión de usuario
        Retorna (success, message, user_data)
        """
        try:
            if not email or not password:
                return False, "Email y contraseña son requeridos", None
            
            # Buscar usuario
            all_records = self.users_sheet.get_all_records()
            user_record = None
            row_index = None
            
            for i, record in enumerate(all_records, start=2):  # Start=2 porque row 1 son headers
                if record.get('email', '').lower() == email.lower():
                    user_record = record
                    row_index = i
                    break
            
            if not user_record:
                return False, "Email o contraseña incorrectos", None
            
            # Verificar contraseña
            if not self.verify_password(password, user_record['password_hash']):
                return False, "Email o contraseña incorrectos", None
            
            # Verificar estado del usuario
            if user_record.get('estado', '').lower() != 'activo':
                return False, "Cuenta desactivada. Contacte al administrador", None
            
            # Actualizar último acceso
            current_time = datetime.now().isoformat()
            self.users_sheet.update(f'L{row_index}', current_time)  # Columna L = ultimo_acceso
            
            # Preparar datos del usuario (sin password_hash)
            user_data = {
                'id': user_record['id'],
                'email': user_record['email'],
                'nombre': user_record['nombre'],
                'apellido': user_record['apellido'],
                'telefono': user_record.get('telefono', ''),
                'fecha_nacimiento': user_record.get('fecha_nacimiento', ''),
                'genero': user_record.get('genero', ''),
                'direccion': user_record.get('direccion', ''),
                'ciudad': user_record.get('ciudad', ''),
                'fecha_registro': user_record.get('fecha_registro', ''),
                'tipo_usuario': user_record['tipo_usuario'],
                'verificado': user_record.get('verificado', 'false'),
                'ultimo_acceso': current_time
            }
            
            logger.info(f"✅ Login exitoso: {email}")
            logger.info(f"🔍 Datos del usuario obtenidos: {user_data}")
            return True, "Login exitoso", user_data
            
        except Exception as e:
            logger.error(f"❌ Error en login: {e}")
            return False, "Error interno del servidor", None

    def get_user_by_id(self, user_id):
        """Obtener usuario por ID"""
        try:
            all_records = self.users_sheet.get_all_records()
            for record in all_records:
                if str(record.get('id', '')) == str(user_id):
                    # Remover password_hash de la respuesta
                    user_data = record.copy()
                    user_data.pop('password_hash', None)
                    return user_data
            return None
        except Exception as e:
            logger.error(f"Error obteniendo usuario: {e}")
            return None

    def update_user_profile(self, user_id, update_data):
        """Actualizar perfil de usuario"""
        try:
            all_records = self.users_sheet.get_all_records()
            row_index = None
            
            for i, record in enumerate(all_records, start=2):
                if str(record.get('id', '')) == str(user_id):
                    row_index = i
                    break
            
            if not row_index:
                return False, "Usuario no encontrado"
            
            # Campos actualizables
            updatable_fields = {
                'nombre': 'D', 'apellido': 'E', 'telefono': 'F', 
                'fecha_nacimiento': 'G', 'genero': 'H', 'direccion': 'I', 
                'ciudad': 'J'
            }
            
            # Actualizar campos
            for field, column in updatable_fields.items():
                if field in update_data:
                    self.users_sheet.update(f'{column}{row_index}', update_data[field])
            
            logger.info(f"✅ Perfil actualizado para usuario ID: {user_id}")
            return True, "Perfil actualizado exitosamente"
            
        except Exception as e:
            logger.error(f"❌ Error actualizando perfil: {e}")
            return False, "Error interno del servidor"

    def change_password(self, user_id, current_password, new_password):
        """Cambiar contraseña de usuario"""
        try:
            # Obtener usuario actual
            all_records = self.users_sheet.get_all_records()
            user_record = None
            row_index = None
            
            for i, record in enumerate(all_records, start=2):
                if str(record.get('id', '')) == str(user_id):
                    user_record = record
                    row_index = i
                    break
            
            if not user_record:
                return False, "Usuario no encontrado"
            
            # Verificar contraseña actual
            if not self.verify_password(current_password, user_record['password_hash']):
                return False, "Contraseña actual incorrecta"
            
            # Validar nueva contraseña
            is_valid, msg = self.validate_password(new_password)
            if not is_valid:
                return False, msg
            
            # Actualizar contraseña
            new_hash = self.hash_password(new_password)
            self.users_sheet.update(f'C{row_index}', new_hash)  # Columna C = password_hash
            
            logger.info(f"✅ Contraseña cambiada para usuario ID: {user_id}")
            return True, "Contraseña actualizada exitosamente"
            
        except Exception as e:
            logger.error(f"❌ Error cambiando contraseña: {e}")
            return False, "Error interno del servidor"

    def get_user_by_email(self, email):
        """Obtener usuario por email"""
        try:
            all_records = self.users_sheet.get_all_records()
            for record in all_records:
                if record.get('email', '').lower() == email.lower():
                    # Remover password_hash de la respuesta
                    user_data = record.copy()
                    user_data.pop('password_hash', None)
                    return user_data
            return None
        except Exception as e:
            logger.error(f"Error obteniendo usuario por email: {e}")
            return None

    def get_user_by_telegram_id(self, telegram_id):
        """Obtener usuario por ID de Telegram"""
        try:
            all_records = self.users_sheet.get_all_records()
            for record in all_records:
                if str(record.get('telegram_id', '')) == str(telegram_id):
                    # Remover password_hash de la respuesta
                    user_data = record.copy()
                    user_data.pop('password_hash', None)
                    return user_data
            return None
        except Exception as e:
            logger.error(f"Error obteniendo usuario por Telegram ID: {e}")
            return None

    def link_telegram_account(self, email, telegram_id, telegram_username=""):
        """Vincular cuenta de Telegram con usuario existente"""
        try:
            all_records = self.users_sheet.get_all_records()
            row_index = None
            user_record = None
            
            # Buscar usuario por email
            for i, record in enumerate(all_records, start=2):
                if record.get('email', '').lower() == email.lower():
                    user_record = record
                    row_index = i
                    break
            
            if not user_record:
                return False, "Usuario no encontrado con ese email", None
            
            # Verificar si ya tiene Telegram vinculado
            if user_record.get('telegram_id'):
                return False, "Esta cuenta ya tiene un Telegram vinculado", None
            
            # Verificar si el Telegram ID ya está en uso
            for record in all_records:
                if str(record.get('telegram_id', '')) == str(telegram_id) and record.get('telegram_id'):
                    return False, "Este Telegram ya está vinculado a otra cuenta", None
            
            # Actualizar las columnas de Telegram
            # Asumo que las columnas están en las posiciones siguientes después de verificado:
            # P = telegram_id, Q = telegram_username
            try:
                self.users_sheet.update(f'P{row_index}', str(telegram_id))  # Columna P = telegram_id
                if telegram_username:
                    self.users_sheet.update(f'Q{row_index}', telegram_username)  # Columna Q = telegram_username
                
                # Actualizar el registro en memoria
                user_record['telegram_id'] = str(telegram_id)
                user_record['telegram_username'] = telegram_username
                
            except Exception as sheet_error:
                logger.warning(f"Error actualizando columnas Telegram, intentando crear: {sheet_error}")
                # Si las columnas no existen, las creamos al final
                self._ensure_telegram_columns()
                # Reintentar
                self.users_sheet.update(f'P{row_index}', str(telegram_id))
                if telegram_username:
                    self.users_sheet.update(f'Q{row_index}', telegram_username)
            
            logger.info(f"✅ Telegram vinculado para usuario: {email}")
            return True, f"Cuenta vinculada exitosamente para {user_record['nombre']} {user_record['apellido']}", user_record
            
        except Exception as e:
            logger.error(f"❌ Error vinculando Telegram: {e}")
            return False, "Error interno del servidor", None
    
    def _ensure_telegram_columns(self):
        """Asegura que las columnas de Telegram existan en la hoja"""
        try:
            # Obtener la primera fila (headers)
            headers = self.users_sheet.row_values(1)
            
            # Verificar si ya existen las columnas
            telegram_columns = ['telegram_id', 'telegram_username']
            missing_columns = []
            
            for col in telegram_columns:
                if col not in headers:
                    missing_columns.append(col)
            
            if missing_columns:
                # Agregar columnas faltantes
                start_col = len(headers) + 1
                for i, col_name in enumerate(missing_columns):
                    col_letter = self._number_to_letter(start_col + i)
                    self.users_sheet.update(f'{col_letter}1', col_name)
                
                logger.info(f"✅ Columnas Telegram agregadas: {missing_columns}")
                
        except Exception as e:
            logger.error(f"Error asegurando columnas Telegram: {e}")
    
    def _number_to_letter(self, n):
        """Convierte un número de columna a letra (1=A, 2=B, etc.)"""
        result = ""
        while n > 0:
            n -= 1
            result = chr(n % 26 + ord('A')) + result
            n //= 26
        return result 