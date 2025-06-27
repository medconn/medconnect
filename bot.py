#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot de Telegram para MedConnect con soporte de archivos múltiples
"""

import os
import json
import logging
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import requests
import time
import random
import re
import uuid
from werkzeug.utils import secure_filename
import socket
from auth_manager import AuthManager
from backend.database.sheets_manager import SheetsManager

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración desde variables de entorno
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GOOGLE_SHEETS_ID = os.environ.get('GOOGLE_SHEETS_ID')
GOOGLE_CREDENTIALS_FILE = os.environ.get('GOOGLE_CREDENTIALS_FILE')

# Configuración de archivos
UPLOAD_FOLDER = 'static/uploads/medical_files'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'gif', 'doc', 'docx', 'txt'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Crear directorio de uploads si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Las credenciales se cargan desde variables de entorno por seguridad
def get_google_credentials():
    """Obtiene las credenciales de Google desde variables de entorno"""
    import json
    import base64
    
    credentials_b64 = os.environ.get('GOOGLE_CREDENTIALS_FILE')
    if not credentials_b64:
        raise ValueError("GOOGLE_CREDENTIALS_FILE no está configurado")
    
    try:
        # Decodificar las credenciales desde base64
        credentials_json = base64.b64decode(credentials_b64).decode('utf-8')
        return json.loads(credentials_json)
    except Exception as e:
        raise ValueError(f"Error decodificando credenciales: {e}")

# Obtener credenciales al inicializar
try:
    GOOGLE_CREDS = get_google_credentials()
except Exception as e:
    logger.error(f"❌ Error cargando credenciales de Google: {e}")
    GOOGLE_CREDS = None

class MedConnectBot:
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.sheets_id = GOOGLE_SHEETS_ID
        self.last_update_id = 0
        self.user_states = {}  # Para rastrear estados de conversación
        self.user_files = {}   # Para almacenar archivos por usuario
        self.upload_folder = UPLOAD_FOLDER
        self.allowed_extensions = ALLOWED_EXTENSIONS
        self.max_file_size = MAX_FILE_SIZE
        self.setup_sheets()
        self.setup_natural_language()
        
    def setup_sheets(self):
        try:
            credentials = Credentials.from_service_account_info(
                GOOGLE_CREDS, scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            self.gc = gspread.authorize(credentials)
            self.spreadsheet = self.gc.open_by_key(self.sheets_id)
            logger.info("✅ Google Sheets conectado")
        except Exception as e:
            logger.error(f"❌ Error Google Sheets: {e}")
            self.gc = None

    def setup_natural_language(self):
        """Configura el sistema de procesamiento de lenguaje natural"""
        
        # Saludos y despedidas
        self.saludos = [
            'hola', 'buenos días', 'buenas tardes', 'buenas noches', 'hey', 'hi',
            'que tal', 'qué tal', 'como estas', 'cómo estás', 'como andas', 
            'cómo andas', 'saludos', 'buenas', 'ola'
        ]
        
        self.despedidas = [
            'chao', 'adiós', 'adios', 'hasta luego', 'nos vemos', 'bye',
            'hasta la vista', 'me voy', 'gracias', 'muchas gracias'
        ]
        
        # Preguntas frecuentes
        self.preguntas_frecuentes = {
            'que puedes hacer': """🤖 <b>¿Qué puedo hacer por ti?</b>

Soy tu asistente médico personal. Puedo ayudarte con:

📋 <b>Registrar consultas médicas</b> (realizadas o futuras)
💊 <b>Gestionar medicamentos</b> y tratamientos  
🩺 <b>Registrar exámenes</b> y resultados
📊 <b>Consultar tu historial</b> médico completo
🔗 <b>Vincular con la plataforma web</b>

💬 También puedo conversar contigo de forma natural. ¡Pregúntame lo que necesites!""",
            
            'como funciona': """⚙️ <b>¿Cómo funciono?</b>

Es muy sencillo:

1️⃣ <b>Escribe palabras clave</b> como "consulta", "medicamento" o "examen"
2️⃣ <b>Sigo las instrucciones</b> que te doy paso a paso
3️⃣ <b>Proporciona los datos</b> en el formato que solicito
4️⃣ <b>¡Listo!</b> Tu información queda guardada de forma segura

🌐 También puedes ver todo en: https://medconnect.cl""",
            
            'es seguro': """🔒 <b>¿Es seguro usar MedConnect?</b>

¡Absolutamente! Tu privacidad es nuestra prioridad:

✅ <b>Datos encriptados</b> y protegidos
✅ <b>Acceso solo tuyo</b> con tu ID personal
✅ <b>Cumplimos normativas</b> de protección de datos
✅ <b>Sin acceso de terceros</b> a tu información médica

Tu información médica está tan segura como en cualquier sistema hospitalario profesional.""",
            
            'cuanto cuesta': """💰 <b>¿Cuánto cuesta MedConnect?</b>

¡Tenemos opciones para todos!

🆓 <b>Plan Gratuito</b>:
   • Registro básico de consultas
   • Historial personal
   • Acceso web limitado

💎 <b>Plan Premium</b>:
   • Funciones avanzadas
   • Recordatorios automáticos
   • Reportes médicos
   • Soporte prioritario

¡Empieza gratis y actualiza cuando quieras!""",
            
            'que es medconnect': """🏥 <b>¿Qué es MedConnect?</b>

Somos tu plataforma integral de salud digital:

📱 <b>Bot de Telegram</b> para registro rápido
🌐 <b>Plataforma web</b> completa
📊 <b>Historial médico</b> organizado
🔔 <b>Recordatorios</b> automáticos
👨‍⚕️ <b>Conexión con profesionales</b>

Hacemos que gestionar tu salud sea fácil, rápido y seguro."""
        }
        
        # Sinónimos para comandos
        self.sinonimos = {
            'consulta': ['cita', 'consulta', 'médico', 'doctor', 'visita médica', 'appointment'],
            'medicamento': ['medicina', 'pastilla', 'medicamento', 'fármaco', 'tratamiento', 'remedio'],
            'examen': ['análisis', 'estudio', 'prueba', 'test', 'examen médico', 'laboratorio'],
            'historial': ['historia', 'registro', 'datos', 'información médica', 'expediente', 'ver', 'consultar', 'mostrar', 'revisar', 'mis datos', 'mi información', 'documentos', 'muestrame', 'muéstrame', 'archivos', 'mis documentos', 'mis archivos']
        }
        
        # Respuestas de agradecimiento
        self.agradecimientos = [
            "¡De nada! 😊 Estoy aquí para ayudarte con tu salud",
            "¡Un placer ayudarte! 🤗 ¿Necesitas algo más?",
            "¡Para eso estoy! 💪 Tu salud es importante",
            "¡Siempre a tu servicio! 🩺 ¿En qué más puedo ayudarte?"
        ]
    
    def cleanup_duplicate_users(self, telegram_id):
        """Limpia usuarios duplicados con el mismo telegram_id"""
        try:
            worksheet = self.spreadsheet.worksheet('Usuarios')
            all_values = worksheet.get_all_values()
            
            if not all_values:
                return
            
            headers = all_values[0]
            users_to_delete = []
            
            # Encontrar usuarios duplicados con mismo telegram_id
            for i, row in enumerate(all_values[1:], 2):
                if len(row) > 16:  # Asegurar que tiene columna telegram_id
                    row_telegram_id = str(row[16]).strip()
                    user_id_col = row[0] if len(row) > 0 else ''
                    email_col = row[1] if len(row) > 1 else ''
                    
                    # Si es un usuario bot duplicado (sin email, con telegram_id)
                    if (row_telegram_id == str(telegram_id) and 
                        user_id_col.startswith('USR_') and 
                        not email_col.strip()):
                        users_to_delete.append(i)
                        logger.info(f"🗑️ Marcando para eliminar usuario duplicado: {user_id_col} (fila {i})")
            
            # Eliminar filas duplicadas (de abajo hacia arriba para no afectar índices)
            for row_index in reversed(users_to_delete):
                worksheet.delete_rows(row_index)
                logger.info(f"✅ Usuario duplicado eliminado (fila {row_index})")
                
        except Exception as e:
            logger.error(f"❌ Error limpiando duplicados: {e}")

    def get_or_create_user(self, user_id, username):
        """Obtiene o crea un usuario en la base de datos"""
        try:
            if not self.gc:
                logger.error("❌ No hay conexión con Google Sheets")
                return None
            
            # Buscar en la hoja de Usuarios
            worksheet = self.spreadsheet.worksheet('Usuarios')
            all_values = worksheet.get_all_values()
            
            logger.info(f"🔍 Buscando usuario con telegram_id: {user_id}")
            logger.info(f"📊 Total de filas en la hoja: {len(all_values)}")
            
            if not all_values:
                logger.warning("⚠️ No hay datos en la hoja de Usuarios")
                return None
            
            headers = all_values[0]
            logger.info(f"📋 Headers disponibles: {headers}")
            
            # Buscar usuario existente por telegram_id en TODAS las filas
            for i, row in enumerate(all_values[1:], 2):  # Empezar desde la fila 2
                if len(row) > 1:
                    # Verificar si el telegram_id coincide (puede estar en diferentes columnas)
                    telegram_id_found = False
                    user_data = {}
                    
                    logger.info(f"🔍 Fila {i}: {row[:5]}...")  # Solo mostrar las primeras 5 columnas para debug
                    
                    # Buscar en las columnas posibles donde puede estar telegram_id
                    for j, header in enumerate(headers):
                        if j < len(row):
                            cell_value = str(row[j]).strip()
                            
                            # Verificar múltiples variaciones de telegram_id
                            header_variations = ['telegram_id', 'telegramid', 'telegram id', 'telegram-id']
                            is_telegram_column = any(header.lower().replace(' ', '').replace('-', '').replace('_', '') == var.replace(' ', '').replace('-', '').replace('_', '') for var in header_variations)
                            
                            if is_telegram_column and cell_value == str(user_id):
                                telegram_id_found = True
                                logger.info(f"✅ Telegram ID encontrado en columna '{header}' (pos {j}): {cell_value}")
                                break
                            # También verificar si está en una columna que parece telegram_id por el contenido
                            elif cell_value == str(user_id) and cell_value.isdigit() and len(cell_value) > 6:
                                telegram_id_found = True
                                logger.info(f"✅ Telegram ID encontrado por contenido en pos {j} (header: '{header}'): {cell_value}")
                                break
                    
                    if telegram_id_found:
                        # Mapear los datos según los headers disponibles
                        for j, header in enumerate(headers):
                            if j < len(row):
                                user_data[header] = row[j]
                        
                        # Determinar user_id y nombre
                        actual_user_id = user_data.get('id') or user_data.get('user_id') or row[0]
                        nombre = user_data.get('nombre', '').strip()
                        apellido = user_data.get('apellido', '').strip()
                        
                        # Si no hay nombre en la columna 'nombre', buscar en otras columnas posibles
                        if not nombre:
                            # Buscar nombre en columnas que podrían contenerlo
                            for key, value in user_data.items():
                                if value and not value.isdigit() and '@' not in value and len(value) > 1:
                                    if key.lower() in ['name', 'first_name', 'nombre_usuario']:
                                        nombre = value.strip()
                                        break
                        
                        # Construir nombre completo si hay apellido
                        if nombre and apellido:
                            full_name = f"{nombre} {apellido}".strip()
                        elif nombre:
                            full_name = nombre
                        else:
                            full_name = username or f'Usuario_{user_id}'
                        
                        logger.info(f"✅ Usuario existente encontrado: {actual_user_id} - {full_name}")
                        logger.info(f"📝 Datos del usuario: {user_data}")
                        
                        return {
                            'user_id': actual_user_id,
                            'nombre': full_name,
                            'telegram_id': str(user_id),
                            'email': user_data.get('email', ''),
                            'telefono': user_data.get('telefono', ''),
                            'tipo_usuario': user_data.get('tipo_usuario', 'paciente')
                        }
            
            # Si no se encontró usuario existente, buscar usuarios sin telegram_id para vincular
            logger.info(f"🔍 No se encontró usuario con telegram_id {user_id}, buscando usuarios sin telegram_id...")
            
            # Buscar usuarios reales (con email) que no tengan telegram_id configurado
            for i, row in enumerate(all_values[1:], 2):
                if len(row) > 1:
                    user_data = {}
                    for j, header in enumerate(headers):
                        if j < len(row):
                            user_data[header] = row[j]
                    
                    # Verificar si es un usuario real (tiene email) sin telegram_id
                    email = user_data.get('email', '').strip()
                    existing_telegram_id = user_data.get('telegram_id', '').strip()
                    nombre = user_data.get('nombre', '').strip()
                    apellido = user_data.get('apellido', '').strip()
                    
                    if email and '@' in email and not existing_telegram_id:
                        # Usuario real sin telegram_id - ofrecer vinculación
                        actual_user_id = user_data.get('id') or row[0]
                        
                        if nombre and apellido:
                            full_name = f"{nombre} {apellido}".strip()
                        elif nombre:
                            full_name = nombre
                        else:
                            full_name = email.split('@')[0]
                        
                        logger.info(f"🔗 Usuario sin telegram_id encontrado: {actual_user_id} - {full_name} ({email})")
                        
                        # Actualizar el telegram_id de este usuario
                        try:
                            # Encontrar la posición de telegram_id en headers
                            if 'telegram_id' in headers:
                                telegram_col = headers.index('telegram_id') + 1  # +1 porque gspread usa 1-indexado
                                worksheet.update_cell(i, telegram_col, str(user_id))
                                logger.info(f"✅ Usuario {actual_user_id} vinculado con telegram_id {user_id}")
                                
                                # Limpiar usuarios duplicados después de vinculación exitosa
                                self.cleanup_duplicate_users(user_id)
                                
                                return {
                                    'user_id': actual_user_id,
                                    'nombre': full_name,
                                    'telegram_id': str(user_id),
                                    'email': email,
                                    'telefono': user_data.get('telefono', ''),
                                    'tipo_usuario': user_data.get('tipo_usuario', 'paciente')
                                }
                        except Exception as e:
                            logger.error(f"❌ Error vinculando usuario: {e}")
                            continue
            
            # Si no hay usuarios para vincular, crear nuevo usuario del bot
            user_id_new = f"USR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Asegurarse de que tenemos todos los headers necesarios
            required_headers = ['user_id', 'telegram_id', 'nombre', 'apellido', 'edad', 'rut', 'telefono', 'email', 'direccion', 'fecha_registro', 'estado', 'plan']
            
            # Agregar headers faltantes si es necesario
            missing_headers = [h for h in required_headers if h not in headers]
            if missing_headers:
                new_headers = headers + missing_headers
                # Actualizar la fila de headers
                worksheet.clear()
                worksheet.append_row(new_headers)
                headers = new_headers
                logger.info(f"📝 Headers actualizados: {missing_headers}")
            
            # Crear datos del nuevo usuario
            new_user_data = [''] * len(headers)
            
            # Mapear datos a las posiciones correctas
            header_map = {
                'user_id': user_id_new,
                'telegram_id': str(user_id),
                'nombre': username or f'Usuario_{user_id}',
                'apellido': '',
                'edad': '',
                'rut': '',
                'telefono': '',
                'email': '',
                'direccion': '',
                'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'estado': 'activo',
                'plan': 'freemium'
            }
            
            for header, value in header_map.items():
                if header in headers:
                    index = headers.index(header)
                    new_user_data[index] = value
            
            worksheet.append_row(new_user_data)
            logger.info(f"✅ Nuevo usuario del bot creado: {user_id_new}")
            
            return {
                'user_id': user_id_new,
                'nombre': username or f'Usuario_{user_id}',
                'telegram_id': str(user_id),
                'email': '',
                'telefono': '',
                'tipo_usuario': 'paciente'
            }
            
        except Exception as e:
            logger.error(f"❌ Error gestionando usuario: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def allowed_file(self, filename):
        """Verifica si el archivo tiene una extensión permitida"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def generate_unique_filename(self, filename):
        """Genera un nombre único para el archivo"""
        ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        return unique_filename
    
    def download_file(self, file_id):
        """Descarga un archivo de Telegram"""
        try:
            # Obtener información del archivo
            file_info_url = f"https://api.telegram.org/bot{self.bot_token}/getFile"
            file_info_response = requests.get(file_info_url, params={'file_id': file_id})
            file_info_response.raise_for_status()
            file_info = file_info_response.json()
            
            if not file_info['ok']:
                return None
                
            file_path = file_info['result']['file_path']
            
            # Descargar el archivo
            download_url = f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}"
            download_response = requests.get(download_url)
            download_response.raise_for_status()
            
            return download_response.content
            
        except Exception as e:
            logger.error(f"❌ Error descargando archivo: {e}")
            return None
    
    def save_file(self, file_content, filename):
        """Guarda el archivo en el servidor"""
        try:
            if not self.allowed_file(filename):
                return None
                
            unique_filename = self.generate_unique_filename(filename)
            filepath = os.path.join(self.upload_folder, unique_filename)
            
            with open(filepath, 'wb') as f:
                f.write(file_content)
                
            return unique_filename
            
        except Exception as e:
            logger.error(f"❌ Error guardando archivo: {e}")
            return None
    
    def process_file(self, user_id, file_info, file_type):
        """Procesa un archivo recibido"""
        try:
            file_id = file_info.get('file_id')
            file_name = file_info.get('file_name', f"archivo_{file_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            # Verificar tamaño del archivo
            file_size = file_info.get('file_size', 0)
            if file_size > self.max_file_size:
                return False, "❌ El archivo es demasiado grande. Máximo 16MB."
            
            # Descargar archivo
            file_content = self.download_file(file_id)
            if not file_content:
                return False, "❌ Error descargando el archivo."
            
            # Guardar archivo
            saved_filename = self.save_file(file_content, file_name)
            if not saved_filename:
                return False, "❌ Tipo de archivo no permitido. Usa: PDF, JPG, PNG, DOC, DOCX, TXT."
            
            # Almacenar en estado del usuario
            if user_id not in self.user_files:
                self.user_files[user_id] = []
                
            file_url = f"/uploads/medical_files/{saved_filename}"
            self.user_files[user_id].append({
                'filename': saved_filename,
                'original_name': file_name,
                'file_url': file_url,
                'file_type': file_type
            })
            
            return True, saved_filename
            
        except Exception as e:
            logger.error(f"❌ Error procesando archivo: {e}")
            return False, "❌ Error interno procesando archivo."
    
    def save_exam_data(self, user_id, exam_data):
        """Guarda los datos del examen en Google Sheets"""
        try:
            if not self.gc:
                logger.error("❌ No hay conexión con Google Sheets")
                return False
            
            worksheet = self.spreadsheet.worksheet('Examenes')
            
            # Obtener archivos del usuario
            user_files = self.user_files.get(user_id, [])
            file_urls = []
            
            if user_files:
                # Crear lista de URLs separadas por comas
                file_urls = [file_info['file_url'] for file_info in user_files]
                file_urls_str = ','.join(file_urls)
                logger.info(f"📎 Archivos adjuntos: {len(user_files)} archivos")
                for file_info in user_files:
                    logger.info(f"   - {file_info['original_name']} ({file_info['file_type']})")
            else:
                file_urls_str = ''
                logger.info("📎 Sin archivos adjuntos")
            
            # Generar ID único para el examen
            exam_id = f"EX_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Preparar datos para insertar
            # ['id', 'patient_id', 'exam_type', 'date', 'results', 'lab', 'doctor', 'file_url', 'status']
            new_row = [
                exam_id,
                user_id,
                exam_data['tipo'],
                exam_data['fecha'],
                exam_data['resultados'],
                exam_data['laboratorio'],
                exam_data['medico'],
                file_urls_str,  # Múltiples URLs separadas por comas
                'Registrado'
            ]
            
            worksheet.append_row(new_row)
            
            # Limpiar archivos del estado del usuario después de guardar
            if user_id in self.user_files:
                del self.user_files[user_id]
            
            logger.info(f"✅ Examen guardado: {exam_id} con {len(user_files)} archivos")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error guardando examen: {e}")
            return False

    def validate_date_format(self, date_str):
        """Valida que la fecha esté en formato DD/MM/YYYY"""
        try:
            if not date_str or '/' not in date_str:
                return False
            
            parts = date_str.split('/')
            if len(parts) != 3:
                return False
            
            day, month, year = parts
            
            # Validar que sean números
            if not (day.isdigit() and month.isdigit() and year.isdigit()):
                return False
            
            day, month, year = int(day), int(month), int(year)
            
            # Validar rangos
            if not (1 <= day <= 31):
                return False
            if not (1 <= month <= 12):
                return False
            if not (1900 <= year <= 2100):
                return False
            
            return True
        except:
            return False

    def validate_time_format(self, time_str):
        """Valida que la hora esté en formato HH:MM"""
        try:
            if not time_str or ':' not in time_str:
                return False
            
            parts = time_str.split(':')
            if len(parts) != 2:
                return False
            
            hour, minute = parts
            
            # Validar que sean números
            if not (hour.isdigit() and minute.isdigit()):
                return False
            
            hour, minute = int(hour), int(minute)
            
            # Validar rangos
            if not (0 <= hour <= 23):
                return False
            if not (0 <= minute <= 59):
                return False
            
            return True
        except:
            return False

    def parse_exam_data(self, text):
        """Parsea los datos del examen desde el texto del usuario"""
        # Eliminar espacios extra y dividir por comas
        parts = [part.strip() for part in text.split(',')]
        
        # Validar que tenemos exactamente 5 partes
        if len(parts) < 5:
            logger.warning(f"❌ Datos insuficientes: {len(parts)}/5 campos requeridos")
            return None
        elif len(parts) > 5:
            logger.warning(f"❌ Demasiados datos: {len(parts)}/5 campos requeridos")
            return None
        
        # Validar que ningún campo esté vacío
        for i, part in enumerate(parts):
            if not part or part.strip() == '':
                logger.warning(f"❌ Campo {i+1} está vacío")
                return None
        
        # Validar formato de fecha (DD/MM/YYYY)
        fecha = parts[1]
        if not self.validate_date_format(fecha):
            logger.warning(f"❌ Formato de fecha incorrecto: {fecha}")
            return None
        
        return {
            'tipo': parts[0],
            'fecha': parts[1],
            'laboratorio': parts[2],
            'resultados': parts[3],
            'medico': parts[4]
        }

    def parse_consulta_realizada(self, text):
        """Parsea los datos de una consulta realizada"""
        parts = [part.strip() for part in text.split(',')]
        
        # Validar que tenemos exactamente 6 partes
        if len(parts) < 6:
            logger.warning(f"❌ Datos insuficientes: {len(parts)}/6 campos requeridos")
            return None
        elif len(parts) > 6:
            logger.warning(f"❌ Demasiados datos: {len(parts)}/6 campos requeridos")
            return None
        
        # Validar que ningún campo esté vacío
        for i, part in enumerate(parts):
            if not part or part.strip() == '':
                logger.warning(f"❌ Campo {i+1} está vacío")
                return None
        
        # Validar formato de fecha
        if not self.validate_date_format(parts[0]):
            logger.warning(f"❌ Formato de fecha incorrecto: {parts[0]}")
            return None
        
        return {
            'fecha': parts[0],
            'especialidad': parts[1],
            'medico': parts[2],
            'centro': parts[3],
            'diagnostico': parts[4],
            'tratamiento': parts[5]
        }

    def parse_consulta_futura(self, text):
        """Parsea los datos de una consulta futura"""
        parts = [part.strip() for part in text.split(',')]
        
        # Validar que tenemos exactamente 6 partes
        if len(parts) < 6:
            logger.warning(f"❌ Datos insuficientes: {len(parts)}/6 campos requeridos")
            return None
        elif len(parts) > 6:
            logger.warning(f"❌ Demasiados datos: {len(parts)}/6 campos requeridos")
            return None
        
        # Validar que ningún campo esté vacío
        for i, part in enumerate(parts):
            if not part or part.strip() == '':
                logger.warning(f"❌ Campo {i+1} está vacío")
                return None
        
        # Validar formato de fecha
        if not self.validate_date_format(parts[0]):
            logger.warning(f"❌ Formato de fecha incorrecto: {parts[0]}")
            return None
        
        # Validar formato de hora (HH:MM)
        if not self.validate_time_format(parts[1]):
            logger.warning(f"❌ Formato de hora incorrecto: {parts[1]}")
            return None
        
        return {
            'fecha': parts[0],
            'hora': parts[1],
            'especialidad': parts[2],
            'medico': parts[3],
            'centro': parts[4],
            'motivo': parts[5]
        }

    def save_consulta_data(self, user_id, consulta_data, tipo):
        """Guarda los datos de la consulta en Google Sheets"""
        try:
            if not self.gc:
                return False
                
            worksheet = self.spreadsheet.worksheet('Consultas')
            
            # Generar ID único para la consulta
            consulta_id = f"CON_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Procesar fecha
            fecha = consulta_data['fecha']
            try:
                # Convertir fecha DD/MM/YYYY a YYYY-MM-DD
                if '/' in fecha:
                    parts = fecha.split('/')
                    if len(parts) == 3:
                        fecha = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
            except:
                fecha = datetime.now().strftime('%Y-%m-%d')
            
            # Estructura correcta según headers reales:
            # ['id', 'patient_id', 'doctor', 'specialty', 'date', 'diagnosis', 'treatment', 'notes', 'status']
            if tipo == 'realizada':
                row_data = [
                    consulta_id,  # id
                    user_id,  # patient_id
                    consulta_data['medico'],  # doctor
                    consulta_data['especialidad'],  # specialty
                    fecha,  # date
                    consulta_data['diagnostico'],  # diagnosis
                    consulta_data['tratamiento'],  # treatment
                    f"Centro: {consulta_data['centro']}",  # notes
                    'completada'  # status
                ]
            else:  # tipo == 'futura'
                row_data = [
                    consulta_id,  # id
                    user_id,  # patient_id
                    consulta_data['medico'],  # doctor
                    consulta_data['especialidad'],  # specialty
                    fecha,  # date
                    consulta_data['motivo'],  # diagnosis (usar motivo como diagnóstico para futuras)
                    f"Hora: {consulta_data['hora']}",  # treatment (usar hora como tratamiento)
                    f"Centro: {consulta_data['centro']}",  # notes
                    'programada'  # status
                ]
            
            worksheet.append_row(row_data)
            logger.info(f"✅ Consulta guardada: {consulta_id} ({tipo})")
            
            # Si es consulta futura, programar recordatorio
            if tipo == 'futura':
                self.schedule_reminder(user_id, consulta_data, consulta_id)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error guardando consulta: {e}")
            return False

    def schedule_reminder(self, user_id, consulta_data, consulta_id):
        """Programa un recordatorio para consulta futura"""
        try:
            # Por ahora solo loggear, la funcionalidad completa requiere un sistema de cron/scheduler
            logger.info(f"📅 Recordatorio programado para {user_id}: {consulta_data['fecha']} {consulta_data['hora']}")
            # TODO: Implementar sistema de recordatorios automáticos
        except Exception as e:
            logger.error(f"❌ Error programando recordatorio: {e}")

    def parse_medicamento_data(self, text):
        """Parsea los datos del medicamento desde el texto del usuario"""
        parts = [part.strip() for part in text.split(',')]
        
        # Validar que tenemos exactamente 5 partes
        if len(parts) < 5:
            logger.warning(f"❌ Datos insuficientes: {len(parts)}/5 campos requeridos")
            return None
        elif len(parts) > 5:
            logger.warning(f"❌ Demasiados datos: {len(parts)}/5 campos requeridos")
            return None
        
        # Validar que ningún campo esté vacío
        for i, part in enumerate(parts):
            if not part or part.strip() == '':
                logger.warning(f"❌ Campo {i+1} está vacío")
                return None
        
        # Validar formato de fecha
        if not self.validate_date_format(parts[4]):
            logger.warning(f"❌ Formato de fecha incorrecto: {parts[4]}")
            return None
        
        return {
            'nombre': parts[0],
            'dosis': parts[1],
            'frecuencia': parts[2],
            'medico': parts[3],
            'fecha_inicio': parts[4]
        }

    def save_medicamento_data(self, user_id, medicamento_data):
        """Guarda los datos del medicamento en Google Sheets"""
        try:
            if not self.gc:
                return False
                
            worksheet = self.spreadsheet.worksheet('Medicamentos')
            
            # Generar ID único para el medicamento
            medicamento_id = f"MED_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Procesar fecha
            fecha_inicio = medicamento_data['fecha_inicio']
            try:
                # Convertir fecha DD/MM/YYYY a YYYY-MM-DD
                if '/' in fecha_inicio:
                    parts = fecha_inicio.split('/')
                    if len(parts) == 3:
                        fecha_inicio = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
            except:
                fecha_inicio = datetime.now().strftime('%Y-%m-%d')
            
            # Estructura correcta según headers reales:
            # ['id', 'patient_id', 'medication', 'dosage', 'frequency', 'start_date', 'end_date', 'prescribed_by', 'status']
            row_data = [
                medicamento_id,  # id
                user_id,  # patient_id
                medicamento_data['nombre'],  # medication
                medicamento_data['dosis'],  # dosage
                medicamento_data['frecuencia'],  # frequency
                fecha_inicio,  # start_date
                '',  # end_date (vacío por defecto)
                medicamento_data['medico'],  # prescribed_by
                'activo'  # status
            ]
            
            worksheet.append_row(row_data)
            logger.info(f"✅ Medicamento guardado: {medicamento_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error guardando medicamento: {e}")
            return False
    
    def log_interaction(self, user_id, username, message, response):
        try:
            if not self.gc:
                return
            worksheet = self.spreadsheet.worksheet('Interacciones_Bot')
            all_values = worksheet.get_all_values()
            next_id = len(all_values)
            
            row_data = [
                next_id, user_id, username or 'Sin username', message, response,
                datetime.now().isoformat(), 'message', 'processed'
            ]
            worksheet.append_row(row_data)
            logger.info(f"✅ Registrado: {user_id}")
        except Exception as e:
            logger.error(f"❌ Error log: {e}")
    
    def send_message(self, chat_id, text):
        """Envía un mensaje de texto con manejo robusto de errores"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
                
                # Timeout más corto para evitar conexiones colgadas
                response = requests.post(url, json=data, timeout=(5, 30))
                response.raise_for_status()
                
                if attempt > 0:
                    logger.info(f"✅ Mensaje enviado después de {attempt + 1} intentos")
                
                return True
                
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"⚠️ Error de conexión enviando mensaje (intento {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Backoff exponencial
                continue
                
            except requests.exceptions.Timeout as e:
                logger.warning(f"⚠️ Timeout enviando mensaje (intento {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                continue
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limit
                    retry_after = int(e.response.headers.get('Retry-After', retry_delay))
                    logger.warning(f"⚠️ Rate limit. Esperando {retry_after}s...")
                    time.sleep(retry_after)
                    if attempt < max_retries - 1:
                        continue
                else:
                    logger.error(f"❌ Error HTTP enviando mensaje: {e}")
                    break
                    
            except Exception as e:
                logger.error(f"❌ Error inesperado enviando mensaje: {e}")
                break
        
        logger.error(f"❌ Falló el envío de mensaje después de {max_retries} intentos")
        return False

    def send_message_with_buttons(self, chat_id, text, inline_keyboard):
        """Envía un mensaje con botones inline con manejo robusto de errores"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                data = {
                    'chat_id': chat_id, 
                    'text': text, 
                    'parse_mode': 'HTML',
                    'reply_markup': {'inline_keyboard': inline_keyboard}
                }
                
                response = requests.post(url, json=data, timeout=(5, 30))
                response.raise_for_status()
                
                if attempt > 0:
                    logger.info(f"✅ Mensaje con botones enviado después de {attempt + 1} intentos")
                
                return True
                
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"⚠️ Error de conexión enviando botones (intento {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                continue
                
            except requests.exceptions.Timeout as e:
                logger.warning(f"⚠️ Timeout enviando botones (intento {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                continue
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    retry_after = int(e.response.headers.get('Retry-After', retry_delay))
                    logger.warning(f"⚠️ Rate limit. Esperando {retry_after}s...")
                    time.sleep(retry_after)
                    if attempt < max_retries - 1:
                        continue
                else:
                    logger.error(f"❌ Error HTTP enviando botones: {e}")
                    break
                    
            except Exception as e:
                logger.error(f"❌ Error inesperado enviando botones: {e}")
                break
        
        logger.error(f"❌ Falló el envío de botones después de {max_retries} intentos")
        return False

    def send_document(self, chat_id, file_path, caption=""):
        """Envía un archivo/documento al chat con manejo robusto de errores"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                url = f"https://api.telegram.org/bot{self.bot_token}/sendDocument"
                
                # Verificar que el archivo existe
                if not os.path.exists(file_path):
                    self.send_message(chat_id, f"❌ Archivo no encontrado: {os.path.basename(file_path)}")
                    return False
                
                # Obtener nombre original del archivo si está disponible
                filename = os.path.basename(file_path)
                
                with open(file_path, 'rb') as file:
                    files = {'document': (filename, file, 'application/octet-stream')}
                    data = {'chat_id': chat_id}
                    if caption:
                        data['caption'] = caption
                        data['parse_mode'] = 'HTML'
                    
                    # Timeout más largo para archivos
                    response = requests.post(url, files=files, data=data, timeout=(30, 120))
                    response.raise_for_status()
                    
                    if attempt > 0:
                        logger.info(f"✅ Archivo enviado después de {attempt + 1} intentos: {filename}")
                    else:
                        logger.info(f"✅ Archivo enviado: {filename}")
                    return True
                    
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"⚠️ Error de conexión enviando archivo (intento {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                continue
                
            except requests.exceptions.Timeout as e:
                logger.warning(f"⚠️ Timeout enviando archivo (intento {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                continue
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    retry_after = int(e.response.headers.get('Retry-After', retry_delay))
                    logger.warning(f"⚠️ Rate limit enviando archivo. Esperando {retry_after}s...")
                    time.sleep(retry_after)
                    if attempt < max_retries - 1:
                        continue
                else:
                    logger.error(f"❌ Error HTTP enviando archivo: {e}")
                    break
                    
            except FileNotFoundError:
                logger.error(f"❌ Archivo no encontrado: {file_path}")
                self.send_message(chat_id, f"❌ Archivo no encontrado: {os.path.basename(file_path)}")
                return False
                
            except Exception as e:
                logger.error(f"❌ Error inesperado enviando archivo: {e}")
                break
        
        logger.error(f"❌ Falló el envío de archivo después de {max_retries} intentos")
        self.send_message(chat_id, f"❌ Error al enviar el archivo. Intenta más tarde.")
        return False

    def handle_callback_query(self, callback_query):
        """Maneja las respuestas de botones inline"""
        try:
            data = callback_query['data']
            chat_id = callback_query['message']['chat']['id']
            user_id = callback_query['from']['id']
            
            # Responder al callback
            self.answer_callback_query(callback_query['id'])
            
            # Procesar diferentes tipos de callbacks
            if data == "main_menu":
                self.show_main_menu(chat_id, user_id)
                
            elif data == "authorize_family":
                self.start_family_authorization(chat_id, user_id)
                
            elif data == "view_family":
                self.show_family_details(chat_id, user_id)
                
            elif data == "switch_user":
                self.show_managed_users(chat_id, user_id)
                
            elif data == "schedule_reminder":
                self.start_reminder_setup(chat_id, user_id)
                
            elif data == "med_reminder":
                self.start_medication_reminder(chat_id, user_id)
                
            elif data == "appointment_reminder":
                self.start_appointment_reminder(chat_id, user_id)
                
            elif data.startswith("switch_to:"):
                target_user_id = data.split(":")[1]
                self.set_managed_user(chat_id, user_id, target_user_id)
                
            elif data.startswith("view_consultations:"):
                target_user_id = data.split(":")[1]
                self.show_consultations(chat_id, user_id, target_user_id)
                
            elif data.startswith("notify_family:"):
                reminder_id = data.split(":")[1]
                self.send_family_notification(chat_id, user_id, reminder_id)
                
            elif data.startswith("perm_"):
                permission_type = data.split("_")[1]
                self.complete_family_authorization(chat_id, user_id, permission_type)
                
            elif data.startswith("freq_"):
                frequency_type = data.split("_")[1]
                self.set_reminder_frequency(chat_id, user_id, frequency_type)
                
            elif data.startswith("reminder_type:"):
                reminder_type = data.split(":")[1]
                self.set_reminder_type(chat_id, user_id, reminder_type)
                
            # Callbacks existentes del sistema de documentos
            elif data.startswith("show_files:"):
                exam_id = data.split(":")[1]
                self.show_exam_files(chat_id, user_id, exam_id)
                
            elif data.startswith("no_files:"):
                self.send_message(chat_id, "📋 Este examen no tiene archivos adjuntos.")
                
            else:
                # Callbacks existentes
                self.handle_existing_callbacks(callback_query)
                
        except Exception as e:
            logger.error(f"❌ Error manejando callback: {e}")
            self.send_message(chat_id, "❌ Error procesando la solicitud.")

    def answer_callback_query(self, callback_query_id, text=""):
        """Responde a un callback query con manejo robusto de errores"""
        max_retries = 2
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                url = f"https://api.telegram.org/bot{self.bot_token}/answerCallbackQuery"
                data = {'callback_query_id': callback_query_id}
                if text:
                    data['text'] = text
                    data['show_alert'] = False
                
                response = requests.post(url, json=data, timeout=(5, 15))
                response.raise_for_status()
                return True
                
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"⚠️ Error de conexión respondiendo callback (intento {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                continue
                
            except requests.exceptions.Timeout as e:
                logger.warning(f"⚠️ Timeout respondiendo callback (intento {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                continue
                
            except Exception as e:
                logger.warning(f"⚠️ Error respondiendo callback: {e}")
                break
        
        return False

    def send_exam_file(self, chat_id, user_id, exam_id, file_index, original_name):
        """Envía un archivo específico de un examen"""
        try:
            # Obtener información del examen
            worksheet = self.spreadsheet.worksheet('Examenes')
            all_values = worksheet.get_all_values()
            
            exam_row = None
            for row in all_values[1:]:
                if (len(row) > 0 and str(row[0]) == str(exam_id) and 
                    len(row) > 1 and str(row[1]) == str(user_id)):
                    exam_row = row
                    break
            
            if not exam_row:
                return False
            
            # Obtener URLs de archivos
            file_urls = exam_row[7] if len(exam_row) > 7 else ''
            if not file_urls or not file_urls.strip():
                return False
            
            urls = [url.strip() for url in file_urls.split(',') if url.strip()]
            
            if file_index >= len(urls):
                return False
            
            file_url = urls[file_index]
            
            # Extraer el nombre del archivo del URL
            if '/' in file_url:
                filename = file_url.split('/')[-1]
            else:
                filename = file_url
            
            # Construir ruta completa del archivo
            file_path = os.path.join('static', 'uploads', 'medical_files', filename)
            
            # Información del examen para el caption
            exam_type = exam_row[2] if len(exam_row) > 2 else 'Examen'
            exam_date = exam_row[3] if len(exam_row) > 3 else 'Sin fecha'
            
            caption = f"📎 <b>{original_name}</b>\n🩺 {exam_type}\n📅 {exam_date}"
            
            return self.send_document(chat_id, file_path, caption)
            
        except Exception as e:
            logger.error(f"❌ Error enviando archivo de examen: {e}")
            return False

    def detect_intent(self, text):
        """Detecta la intención del usuario basado en el texto"""
        text_lower = text.lower().strip()
        
        # Detectar saludos
        if any(saludo in text_lower for saludo in self.saludos):
            return 'saludo'
        
        # Detectar despedidas
        if any(despedida in text_lower for despedida in self.despedidas):
            return 'despedida'
        
        # Detectar agradecimientos
        if 'gracias' in text_lower:
            return 'agradecimiento'
        
        # Detectar preguntas frecuentes
        for key in self.preguntas_frecuentes.keys():
            key_words = key.split()
            if all(word in text_lower for word in key_words):
                return f'pregunta:{key}'
        
        # Detectar comandos por sinónimos
        for comando, sinonimos in self.sinonimos.items():
            if any(sinonimo in text_lower for sinonimo in sinonimos):
                return f'comando:{comando}'
        
        # Detectar preguntas generales
        palabras_pregunta = ['qué', 'que', 'cómo', 'como', 'cuál', 'cual', 'dónde', 'donde', 
                           'cuándo', 'cuando', 'por qué', 'porque', 'para qué', 'ayuda']
        if any(palabra in text_lower for palabra in palabras_pregunta):
            return 'pregunta_general'
        
        return 'desconocido'

    def generate_natural_response(self, intent, user_name=""):
        """Genera respuestas naturales basadas en la intención"""
        import random
        
        if intent == 'saludo':
            saludos_respuesta = [
                f"¡Hola{' ' + user_name if user_name else ''}! 👋 ¿En qué puedo ayudarte hoy?",
                f"¡Buenos días{' ' + user_name if user_name else ''}! 🌅 ¿Cómo está tu salud?",
                f"¡Hola{' ' + user_name if user_name else ''}! 😊 Estoy aquí para ayudarte con tus consultas médicas",
                f"¡Qué tal{' ' + user_name if user_name else ''}! 🩺 ¿Necesitas registrar algo en tu historial?"
            ]
            return random.choice(saludos_respuesta)
        
        elif intent == 'despedida':
            despedidas_respuesta = [
                "¡Hasta luego! 👋 Cuídate mucho y recuerda mantener tu salud al día",
                "¡Nos vemos! 😊 No olvides registrar tus próximas consultas",
                "¡Adiós! 🌟 Estoy aquí cuando me necesites para tu salud",
                "¡Que tengas un excelente día! 💪 Tu salud es lo más importante"
            ]
            return random.choice(despedidas_respuesta)
        
        elif intent == 'agradecimiento':
            return random.choice(self.agradecimientos)
        
        elif intent.startswith('pregunta:'):
            key = intent.replace('pregunta:', '')
            return self.preguntas_frecuentes.get(key, "🤔 Interesante pregunta. ¿Podrías ser más específico?")
        
        elif intent.startswith('comando:'):
            comando = intent.replace('comando:', '')
            return f"comando_{comando}"  # Será procesado por la lógica existente
        
        elif intent == 'pregunta_general':
            return """🤖 <b>¡Buena pregunta!</b>

Puedo ayudarte con muchas cosas relacionadas con tu salud:

❓ <b>Pregúntame sobre:</b>
• "¿Qué puedes hacer?"
• "¿Cómo funciona MedConnect?"
• "¿Es seguro?"
• "¿Cuánto cuesta?"

📋 <b>O dime directamente:</b>
• "Quiero registrar una consulta"
• "Necesito anotar un medicamento"
• "Tengo resultados de exámenes"

💬 ¡También puedes conversar conmigo de forma natural!"""
        
        else:
            return """🤖 <b>No estoy seguro de entenderte</b>

¿Podrías intentar con:
• Una pregunta más específica
• Palabras como "consulta", "medicamento" o "examen"
• Preguntarme "¿qué puedes hacer?"

💡 <b>Tip:</b> Puedes hablarme de forma natural, ¡entiendo el lenguaje cotidiano!"""

    def process_message(self, message):
        """Procesa mensajes de texto recibidos"""
        try:
            text = message.get('text', '').lower().strip()
            chat_id = message['chat']['id']
            user_id = message['from']['id']
            
            # Verificar si el usuario está registrado
            if not self.is_user_registered(user_id):
                self.send_message(chat_id, "👋 ¡Hola! Para usar MedConnect necesitas registrarte primero.\n\n🌐 Visita: https://medconnect.cl/register")
                return
            
            # Obtener información del usuario
            user_data = self.get_user_data(user_id)
            user_name = user_data.get('nombre', 'Usuario')
            
            # Verificar si es un familiar autorizado gestionando a otro usuario
            managing_user = self.get_managing_user(user_id)
            if managing_user:
                # Notificar a familiares sobre actividad del usuario principal
                self.notify_family_activity(managing_user['id'], f"📱 {user_name} está usando MedConnect", user_id)
            
            # Procesar comandos especiales primero
            if text.startswith('/'):
                self.handle_command(chat_id, user_id, text)
                return
            
            # Procesar respuestas contextuales
            if hasattr(self, 'user_contexts') and user_id in self.user_contexts:
                self.handle_contextual_response(chat_id, user_id, text)
                return
            
            # Menú principal
            if any(word in text for word in ['hola', 'inicio', 'menu', 'empezar', 'start']):
                self.show_main_menu(chat_id, user_id)
                return
            
            # Gestión de familiares
            if any(word in text for word in ['familiares', 'familia', 'autorizar', 'permisos']):
                self.show_family_menu(chat_id, user_id)
                return
            
            # Gestión de notificaciones
            if any(word in text for word in ['notificaciones', 'avisos', 'recordatorios']):
                self.show_notifications_menu(chat_id, user_id)
                return
            
            # Ver información médica (propia o de familiar autorizado)
            if any(word in text for word in ['historial', 'consultas', 'documentos', 'muestrame', 'muéstrame', 'archivos', 'mis documentos', 'mis archivos']):
                self.show_medical_info_menu(chat_id, user_id)
                return
            
            # Registrar información médica
            if any(word in text for word in ['registrar', 'agregar', 'nueva consulta', 'consulta']):
                self.show_register_menu(chat_id, user_id)
                return
            
            # Cambiar usuario gestionado (para familiares autorizados)
            if text.startswith('gestionar '):
                target_name = text.replace('gestionar ', '').strip()
                self.switch_managed_user(chat_id, user_id, target_name)
                return
            
            # Procesar información médica con formato específico
            if self.is_medical_data(text):
                self.process_medical_data(chat_id, user_id, text)
                return
            
            # Respuesta por defecto
            self.send_message(chat_id, "🤖 No estoy seguro de entenderte. Escribe 'menu' para ver las opciones disponibles.")
            
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje: {e}")
            self.send_message(chat_id, "❌ Error procesando tu mensaje. Intenta más tarde.")

    def show_family_menu(self, chat_id, user_id):
        """Muestra el menú de gestión familiar"""
        try:
            # Obtener familiares autorizados y usuarios que este usuario puede gestionar
            user_data = self.get_user_data(user_id)
            actual_user_id = user_data.get('user_id') or user_data.get('id')
            
            authorized_family = self.sheets_manager.get_familiares_autorizados(actual_user_id)
            managed_users = self.sheets_manager.get_managed_users(str(user_id))
            
            menu_text = "👨‍👩‍👧‍👦 <b>Gestión Familiar</b>\n\n"
            
            if managed_users:
                menu_text += "👥 <b>Puedes gestionar:</b>\n"
                for i, user in enumerate(managed_users, 1):
                    menu_text += f"{i}. {user['nombre']} {user.get('apellido', '')} ({user['parentesco']})\n"
                menu_text += "\n"
            
            if authorized_family:
                menu_text += "✅ <b>Familiares autorizados:</b>\n"
                for familiar in authorized_family:
                    menu_text += f"• {familiar['nombre_familiar']} ({familiar['parentesco']})\n"
                menu_text += "\n"
            
            if not managed_users and not authorized_family:
                menu_text += "👨‍👩‍👧‍👦 No tienes familiares configurados aún.\n\n"
            
            buttons = [
                [{"text": "👤 Autorizar Familiar", "callback_data": "authorize_family"}],
                [{"text": "👥 Ver Familiares", "callback_data": "view_family"}],
                [{"text": "🔄 Cambiar Usuario Gestionado", "callback_data": "switch_user"}],
                [{"text": "🏠 Menú Principal", "callback_data": "main_menu"}]
            ]
            
            self.send_message_with_buttons(chat_id, menu_text, buttons)
            
        except Exception as e:
            logger.error(f"❌ Error mostrando menú familiar: {e}")
            self.send_message(chat_id, "❌ Error mostrando menú familiar.")

    def show_notifications_menu(self, chat_id, user_id):
        """Muestra el menú de notificaciones"""
        try:
            user_data = self.get_user_data(user_id)
            managing_user = self.get_managing_user(user_id)
            
            if managing_user:
                menu_text = f"🔔 <b>Notificaciones para {managing_user['nombre']}</b>\n\n"
            else:
                menu_text = f"🔔 <b>Tus Notificaciones</b>\n\n"
            
            # Obtener recordatorios activos
            active_reminders = self.get_active_reminders(managing_user['id'] if managing_user else str(user_id))
            
            if active_reminders:
                menu_text += "⏰ <b>Recordatorios activos:</b>\n"
                for reminder in active_reminders[:5]:
                    menu_text += f"• {reminder['tipo']}: {reminder['mensaje']}\n"
                menu_text += "\n"
            
            buttons = [
                [{"text": "⏰ Programar Recordatorio", "callback_data": "schedule_reminder"}],
                [{"text": "💊 Recordatorio Medicamento", "callback_data": "med_reminder"}],
                [{"text": "🏥 Recordatorio Cita Médica", "callback_data": "appointment_reminder"}],
                [{"text": "📋 Ver Todos los Recordatorios", "callback_data": "view_all_reminders"}],
                [{"text": "🏠 Menú Principal", "callback_data": "main_menu"}]
            ]
            
            self.send_message_with_buttons(chat_id, menu_text, buttons)
            
        except Exception as e:
            logger.error(f"❌ Error mostrando menú de notificaciones: {e}")
            self.send_message(chat_id, "❌ Error mostrando menú de notificaciones.")

    def show_medical_info_menu(self, chat_id, user_id):
        """Muestra el menú de información médica (propia o de familiar)"""
        try:
            managing_user = self.get_managing_user(user_id)
            
            if managing_user:
                menu_text = f"📋 <b>Información Médica de {managing_user['nombre']}</b>\n\n"
                target_user_id = managing_user['id']
            else:
                menu_text = "📋 <b>Tu Información Médica</b>\n\n"
                target_user_id = str(user_id)
            
            # Obtener resumen médico
            medical_summary = self.get_medical_summary(target_user_id)
            
            menu_text += f"📊 <b>Resumen:</b>\n"
            menu_text += f"• Consultas: {medical_summary.get('total_consultas', 0)}\n"
            menu_text += f"• Medicamentos activos: {medical_summary.get('medicamentos_activos', 0)}\n"
            menu_text += f"• Exámenes: {medical_summary.get('total_examenes', 0)}\n\n"
            
            buttons = [
                [{"text": "🏥 Ver Consultas", "callback_data": f"view_consultations:{target_user_id}"}],
                [{"text": "💊 Ver Medicamentos", "callback_data": f"view_medications:{target_user_id}"}],
                [{"text": "📄 Ver Documentos", "callback_data": f"view_documents:{target_user_id}"}],
                [{"text": "📊 Resumen Completo", "callback_data": f"full_summary:{target_user_id}"}],
                [{"text": "🏠 Menú Principal", "callback_data": "main_menu"}]
            ]
            
            self.send_message_with_buttons(chat_id, menu_text, buttons)
            
        except Exception as e:
            logger.error(f"❌ Error mostrando información médica: {e}")
            self.send_message(chat_id, "❌ Error mostrando información médica.")

    def handle_contextual_response(self, chat_id, user_id, text):
        """Maneja respuestas contextuales según el estado del usuario"""
        try:
            context = self.user_contexts[user_id]
            
            if context['action'] == 'authorize_family':
                self.handle_family_authorization_step(chat_id, user_id, text, context)
                
            elif context['action'] in ['schedule_reminder', 'med_reminder', 'appointment_reminder', 'general_reminder']:
                self.handle_reminder_setup_step(chat_id, user_id, text, context)
                
            elif context['action'] == 'medical_registration':
                self.handle_medical_registration_step(chat_id, user_id, text, context)
                
        except Exception as e:
            logger.error(f"❌ Error manejando respuesta contextual: {e}")
            self.send_message(chat_id, "❌ Error procesando tu respuesta.")

    def handle_family_authorization_step(self, chat_id, user_id, text, context):
        """Maneja los pasos de autorización familiar"""
        try:
            if context['step'] == 'name':
                context['name'] = text
                context['step'] = 'relationship'
                self.send_message(chat_id, f"✅ Nombre: <b>{text}</b>\n\n"
                                         "📝 <b>Paso 2:</b> ¿Qué parentesco tiene contigo?\n"
                                         "(Ejemplo: hijo, hija, esposo, esposa, madre, padre, hermano, hermana)")
                
            elif context['step'] == 'relationship':
                context['relationship'] = text
                context['step'] = 'phone'
                self.send_message(chat_id, f"✅ Parentesco: <b>{text}</b>\n\n"
                                         "📝 <b>Paso 3:</b> Número de teléfono del familiar\n"
                                         "(Ejemplo: +56912345678)")
                
            elif context['step'] == 'phone':
                context['phone'] = text
                context['step'] = 'permissions'
                
                buttons = [
                    [{"text": "👀 Solo Ver", "callback_data": "perm_read"}],
                    [{"text": "✏️ Ver y Editar", "callback_data": "perm_write"}],
                    [{"text": "👑 Control Total", "callback_data": "perm_admin"}]
                ]
                
                self.send_message_with_buttons(chat_id, 
                    f"✅ Teléfono: <b>{text}</b>\n\n"
                    "📝 <b>Paso 4:</b> ¿Qué permisos quieres darle?\n\n"
                    "👀 <b>Solo Ver:</b> Puede ver tu información médica\n"
                    "✏️ <b>Ver y Editar:</b> Puede ver y agregar información\n"
                    "👑 <b>Control Total:</b> Puede gestionar todo (recomendado para cuidadores)", 
                    buttons)
                
            elif context['step'] == 'telegram_id':
                telegram_id = text.strip()
                
                if telegram_id.lower() == 'saltar':
                    telegram_id = ''
                
                # Finalizar autorización
                user_data = self.get_user_data(user_id)
                actual_user_id = user_data.get('user_id') or user_data.get('id')
                
                family_data = {
                    'nombre_familiar': context['name'],
                    'parentesco': context['relationship'],
                    'telefono': context['phone'],
                    'telegram_id': telegram_id,
                    'permisos': context['permissions'],
                    'notificaciones': 'true' if telegram_id else 'false'
                }
                
                familiar_id = self.sheets_manager.authorize_family_member(actual_user_id, family_data)
                
                success_text = f"✅ <b>Familiar autorizado exitosamente</b>\n\n"
                success_text += f"👤 Nombre: {context['name']}\n"
                success_text += f"👨‍👩‍👧‍👦 Parentesco: {context['relationship']}\n"
                success_text += f"📞 Teléfono: {context['phone']}\n"
                success_text += f"🔑 Permisos: {context['permissions']}\n"
                
                if telegram_id:
                    success_text += f"📱 Telegram ID: {telegram_id}\n"
                    success_text += f"🔔 Recibirá notificaciones: Sí\n"
                else:
                    success_text += f"🔔 Recibirá notificaciones: No\n"
                
                success_text += f"\n💡 ID del familiar: {familiar_id}"
                
                self.send_message(chat_id, success_text)
                
                # Limpiar contexto
                del self.user_contexts[user_id]
                
                # Mostrar menú familiar
                self.show_family_menu(chat_id, user_id)
                
        except Exception as e:
            logger.error(f"❌ Error en paso de autorización: {e}")
            logger.error(f"❌ Error en configuración de recordatorio: {e}")
            self.send_message(chat_id, "❌ Error configurando recordatorio.")

    def get_updates(self):
        """Obtiene actualizaciones del bot con manejo robusto de errores"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
            params = {'offset': self.last_update_id + 1, 'timeout': 30}
            
            # Configurar timeout más corto para evitar conexiones colgadas
            response = requests.get(url, params=params, timeout=(10, 30))
            response.raise_for_status()
            
            data = response.json()
            
            if data['ok']:
                return data['result']
            else:
                logger.error(f"❌ Error en respuesta de Telegram: {data}")
                return []
                
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"⚠️ Error de conexión (reintentando): {str(e)[:100]}...")
            return []
        except requests.exceptions.Timeout as e:
            logger.warning(f"⚠️ Timeout de conexión: {str(e)[:100]}...")
            return []
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ Error HTTP: {e}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error de request: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error inesperado obteniendo updates: {e}")
            return []

    def check_internet_connection(self):
        """Verifica si hay conexión a internet"""
        try:
            # Intentar conectar a un servidor DNS público
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            return True
        except OSError:
            return False

    def wait_for_connection(self, max_wait=300):
        """Espera hasta que haya conexión a internet"""
        wait_time = 5
        total_waited = 0
        
        while total_waited < max_wait:
            if self.check_internet_connection():
                logger.info("✅ Conexión a internet restaurada")
                return True
            
            logger.warning(f"⚠️ Sin conexión a internet. Esperando {wait_time}s...")
            time.sleep(wait_time)
            total_waited += wait_time
            
            # Incrementar tiempo de espera gradualmente (backoff)
            wait_time = min(wait_time * 1.2, 60)  # Máximo 60 segundos
        
        logger.error(f"❌ Sin conexión después de {max_wait} segundos")
        return False
    
    def run(self):
        logger.info("🚀 MedConnect Bot iniciado")
        logger.info("📱 https://t.me/medconnect_bot")
        logger.info("⏹️  Ctrl+C para detener")
        
        consecutive_errors = 0
        max_consecutive_errors = 10
        
        try:
            while True:
                # Verificar conexión antes de intentar obtener updates
                if not self.check_internet_connection():
                    logger.warning("⚠️ Sin conexión a internet detectada")
                    if not self.wait_for_connection():
                        continue
                
                updates = self.get_updates()
                
                # Si obtuvimos updates exitosamente, resetear contador de errores
                if updates or updates == []:  # Lista vacía también es éxito
                    consecutive_errors = 0
                
                for update in updates:
                    try:
                        self.last_update_id = update['update_id']
                        
                        # Procesar mensajes de texto y archivos
                        if 'message' in update:
                            message = update['message']
                            user_info = f"{message['from'].get('username', 'usuario')} ({message['from']['id']})"
                            logger.info(f"📨 Mensaje de {user_info}: {message.get('text', '[archivo]')}")
                            self.process_message(message)
                        
                        # Procesar callbacks de botones inline
                        elif 'callback_query' in update:
                            callback_query = update['callback_query']
                            user_info = f"{callback_query['from'].get('username', 'usuario')} ({callback_query['from']['id']})"
                            logger.info(f"🔘 Callback de {user_info}: {callback_query['data']}")
                            self.handle_callback_query(callback_query)
                            
                    except Exception as e:
                        logger.error(f"❌ Error procesando update {update.get('update_id', 'unknown')}: {e}")
                        continue
                
                # Si no obtuvimos updates, incrementar contador de errores
                if not updates and updates != []:
                    consecutive_errors += 1
                    
                    if consecutive_errors >= max_consecutive_errors:
                        logger.error(f"❌ Demasiados errores consecutivos ({consecutive_errors}). Esperando...")
                        if not self.wait_for_connection(60):  # Esperar máximo 1 minuto
                            consecutive_errors = 0  # Resetear para intentar de nuevo
                
                # Pausa adaptativa basada en errores
                if consecutive_errors > 0:
                    sleep_time = min(consecutive_errors * 2, 30)  # Máximo 30 segundos
                    logger.info(f"⏳ Pausa de {sleep_time}s debido a errores ({consecutive_errors})")
                    time.sleep(sleep_time)
                else:
                    time.sleep(1)  # Pausa normal
                
        except KeyboardInterrupt:
            logger.info("🛑 Bot detenido por el usuario")
        except Exception as e:
            logger.error(f"❌ Error crítico en bucle principal: {e}")
            logger.info("🔄 Intentando reiniciar...")
            # Esperar un poco antes de que el proceso pueda reiniciarse
            time.sleep(5)

    def show_exam_files(self, chat_id, user_id, exam_id):
        """Muestra los archivos de un examen específico con botones para descargar"""
        try:
            # Obtener información del examen
            worksheet = self.spreadsheet.worksheet('Examenes')
            all_values = worksheet.get_all_values()
            
            exam_row = None
            for row in all_values[1:]:
                if (len(row) > 0 and str(row[0]) == str(exam_id) and 
                    len(row) > 1 and str(row[1]) == str(user_id)):
                    exam_row = row
                    break
            
            if not exam_row:
                return f"❌ No se encontró el examen con ID: {exam_id}"
            
            # Obtener información del examen
            exam_type = exam_row[2] if len(exam_row) > 2 else 'Examen'
            exam_date = exam_row[3] if len(exam_row) > 3 else 'Sin fecha'
            file_urls = exam_row[7] if len(exam_row) > 7 else ''
            
            if not file_urls or not file_urls.strip():
                return f"📎 <b>El examen {exam_type}</b> no tiene archivos adjuntos."
            
            urls = [url.strip() for url in file_urls.split(',') if url.strip()]
            
            if not urls:
                return f"📎 <b>El examen {exam_type}</b> no tiene archivos válidos."
            
            # Crear mensaje con información del examen
            message_text = f"""📎 <b>Archivos del Examen</b>

🩺 <b>Tipo:</b> {exam_type}
📅 <b>Fecha:</b> {exam_date}
📂 <b>Total de archivos:</b> {len(urls)}

💾 <b>Selecciona un archivo para descargar:</b>"""
            
            # Crear botones inline para cada archivo
            inline_keyboard = []
            
            for i, url in enumerate(urls):
                # Extraer nombre del archivo
                if '/' in url:
                    filename = url.split('/')[-1]
                else:
                    filename = url
                
                # Determinar tipo de archivo y emoji
                ext = filename.split('.')[-1].lower() if '.' in filename else 'unknown'
                
                if ext == 'pdf':
                    emoji = "📄"
                    file_type = "PDF"
                elif ext in ['jpg', 'jpeg', 'png', 'gif']:
                    emoji = "🖼️"
                    file_type = "Imagen"
                elif ext in ['doc', 'docx']:
                    emoji = "📝"
                    file_type = "Word"
                elif ext in ['dcm', 'dicom']:
                    emoji = "🩻"
                    file_type = "DICOM"
                else:
                    emoji = "📎"
                    file_type = ext.upper()
                
                # Crear texto del botón más descriptivo
                button_text = f"{emoji} Archivo {i+1} ({file_type})"
                callback_data = f"file:{exam_id}|{i}|{file_type}_{i+1}"
                
                inline_keyboard.append([{"text": button_text, "callback_data": callback_data}])
            
            # Agregar botón para cerrar
            inline_keyboard.append([{"text": "❌ Cerrar", "callback_data": "close_files"}])
            
            # Enviar mensaje con botones
            success = self.send_message_with_buttons(chat_id, message_text, inline_keyboard)
            
            if success:
                return ""  # No enviar mensaje adicional ya que se envió con botones
            else:
                return "❌ Error al mostrar los archivos. Intenta más tarde."
                
        except Exception as e:
            logger.error(f"❌ Error mostrando archivos del examen: {e}")
            return "❌ Error al acceder a los archivos del examen."

if __name__ == "__main__":
    bot = MedConnectBot()
    bot.run() 