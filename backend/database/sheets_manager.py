"""
Gestor de Google Sheets para MedConnect
Maneja todas las operaciones CRUD con la base de datos en Google Sheets
"""
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Any
from config import Config

logger = logging.getLogger(__name__)

class SheetsManager:
    def __init__(self):
        """Inicializa la conexión con Google Sheets"""
        self.gc = None
        self.spreadsheet = None
        self.connect()
    
    def connect(self):
        """Establece conexión con Google Sheets"""
        try:
            # Configurar credenciales
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = Credentials.from_service_account_file(
                Config.GOOGLE_CREDENTIALS_FILE, 
                scopes=scopes
            )
            
            self.gc = gspread.authorize(creds)
            self.spreadsheet = self.gc.open_by_key(Config.GOOGLE_SHEETS_ID)
            
            logger.info("Conexión exitosa con Google Sheets")
            
        except Exception as e:
            logger.error(f"Error conectando con Google Sheets: {e}")
            raise
    
    def get_worksheet(self, sheet_name: str):
        """Obtiene una hoja específica del spreadsheet"""
        try:
            return self.spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            # Si no existe, la creamos
            return self.create_worksheet(sheet_name)
    
    def create_worksheet(self, sheet_name: str):
        """Crea una nueva hoja con headers según el tipo"""
        headers = self.get_sheet_headers(sheet_name)
        worksheet = self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=len(headers))
        
        # Agregar headers
        worksheet.append_row(headers)
        
        logger.info(f"Hoja '{sheet_name}' creada exitosamente")
        return worksheet
    
    def get_sheet_headers(self, sheet_name: str) -> List[str]:
        """Define los headers para cada tipo de hoja"""
        headers_map = {
            'Usuarios': [
                'user_id', 'telegram_id', 'nombre', 'apellido', 'edad', 
                'rut', 'telefono', 'email', 'direccion', 'fecha_registro', 
                'estado', 'plan'
            ],
            'Atenciones_Medicas': [
                'atencion_id', 'user_id', 'fecha', 'hora', 'tipo_atencion',
                'especialidad', 'profesional', 'centro_salud', 'diagnostico',
                'tratamiento', 'observaciones', 'proxima_cita', 'estado'
            ],
            'Medicamentos': [
                'medicamento_id', 'user_id', 'atencion_id', 'nombre_medicamento',
                'dosis', 'frecuencia', 'duracion', 'indicaciones',
                'fecha_inicio', 'fecha_fin', 'estado'
            ],
            'Examenes': [
                'examen_id', 'user_id', 'atencion_id', 'tipo_examen',
                'nombre_examen', 'fecha_solicitud', 'fecha_realizacion',
                'resultado', 'archivo_url', 'observaciones', 'estado'
            ],
            'Familiares_Autorizados': [
                'familiar_id', 'user_id', 'nombre_familiar', 'parentesco',
                'telefono', 'email', 'telegram_id', 'permisos', 
                'fecha_autorizacion', 'estado', 'notificaciones'
            ],
            'Recordatorios': [
                'reminder_id', 'user_id', 'tipo', 'titulo', 'mensaje',
                'fecha_programada', 'hora_programada', 'frecuencia',
                'notificar_familiares', 'fecha_creacion', 'estado'
            ],
            'Logs_Acceso': [
                'log_id', 'user_id', 'accion', 'detalle', 'ip_address',
                'timestamp', 'resultado'
            ]
        }
        
        return headers_map.get(sheet_name, ['id', 'data', 'timestamp'])
    
    # CRUD Operations para Usuarios
    def create_user(self, user_data: Dict[str, Any]) -> str:
        """Crea un nuevo usuario en la base de datos"""
        try:
            worksheet = self.get_worksheet('Usuarios')
            
            # Generar ID único
            user_id = f"USR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            row_data = [
                user_id,
                user_data.get('telegram_id', ''),
                user_data.get('nombre', ''),
                user_data.get('apellido', ''),
                user_data.get('edad', ''),
                user_data.get('rut', ''),
                user_data.get('telefono', ''),
                user_data.get('email', ''),
                user_data.get('direccion', ''),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'activo',
                'freemium'
            ]
            
            worksheet.append_row(row_data)
            
            logger.info(f"Usuario {user_id} creado exitosamente")
            return user_id
            
        except Exception as e:
            logger.error(f"Error creando usuario: {e}")
            raise
    
    def get_user_by_telegram_id(self, telegram_id: str) -> Optional[Dict[str, Any]]:
        """Busca un usuario por su Telegram ID"""
        try:
            worksheet = self.get_worksheet('Usuarios')
            records = worksheet.get_all_records()
            
            for record in records:
                if str(record.get('telegram_id')) == str(telegram_id):
                    return record
            
            return None
            
        except Exception as e:
            logger.error(f"Error buscando usuario: {e}")
            return None
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Actualiza los datos de un usuario"""
        try:
            worksheet = self.get_worksheet('Usuarios')
            records = worksheet.get_all_records()
            
            for i, record in enumerate(records, start=2):  # Start from row 2 (after headers)
                if record.get('user_id') == user_id:
                    # Actualizar campos específicos
                    for key, value in update_data.items():
                        if key in record:
                            col_index = list(record.keys()).index(key) + 1
                            worksheet.update_cell(i, col_index, value)
                    
                    logger.info(f"Usuario {user_id} actualizado exitosamente")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error actualizando usuario: {e}")
            return False
    
    # CRUD Operations para Atenciones Médicas
    def create_atencion(self, atencion_data: Dict[str, Any]) -> str:
        """Registra una nueva atención médica"""
        try:
            worksheet = self.get_worksheet('Atenciones_Medicas')
            
            # Generar ID único
            atencion_id = f"ATN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            row_data = [
                atencion_id,
                atencion_data.get('user_id', ''),
                atencion_data.get('fecha', ''),
                atencion_data.get('hora', ''),
                atencion_data.get('tipo_atencion', ''),
                atencion_data.get('especialidad', ''),
                atencion_data.get('profesional', ''),
                atencion_data.get('centro_salud', ''),
                atencion_data.get('diagnostico', ''),
                atencion_data.get('tratamiento', ''),
                atencion_data.get('observaciones', ''),
                atencion_data.get('proxima_cita', ''),
                'registrada'
            ]
            
            worksheet.append_row(row_data)
            
            logger.info(f"Atención {atencion_id} registrada exitosamente")
            return atencion_id
            
        except Exception as e:
            logger.error(f"Error registrando atención: {e}")
            raise
    
    def get_user_atenciones(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtiene todas las atenciones de un usuario"""
        try:
            worksheet = self.get_worksheet('Atenciones_Medicas')
            records = worksheet.get_all_records()
            
            user_atenciones = [
                record for record in records 
                if record.get('user_id') == user_id
            ]
            
            # Ordenar por fecha más reciente
            user_atenciones.sort(
                key=lambda x: datetime.strptime(x.get('fecha', '1900-01-01'), '%Y-%m-%d'),
                reverse=True
            )
            
            return user_atenciones
            
        except Exception as e:
            logger.error(f"Error obteniendo atenciones: {e}")
            return []
    
    # CRUD Operations para Medicamentos
    def create_medicamento(self, medicamento_data: Dict[str, Any]) -> str:
        """Registra un nuevo medicamento"""
        try:
            worksheet = self.get_worksheet('Medicamentos')
            
            # Generar ID único
            medicamento_id = f"MED_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            row_data = [
                medicamento_id,
                medicamento_data.get('user_id', ''),
                medicamento_data.get('atencion_id', ''),
                medicamento_data.get('nombre_medicamento', ''),
                medicamento_data.get('dosis', ''),
                medicamento_data.get('frecuencia', ''),
                medicamento_data.get('duracion', ''),
                medicamento_data.get('indicaciones', ''),
                medicamento_data.get('fecha_inicio', ''),
                medicamento_data.get('fecha_fin', ''),
                'activo'
            ]
            
            worksheet.append_row(row_data)
            
            logger.info(f"Medicamento {medicamento_id} registrado exitosamente")
            return medicamento_id
            
        except Exception as e:
            logger.error(f"Error registrando medicamento: {e}")
            raise
    
    def get_user_medicamentos_activos(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtiene los medicamentos activos de un usuario"""
        try:
            worksheet = self.get_worksheet('Medicamentos')
            records = worksheet.get_all_records()
            
            medicamentos_activos = []
            today = datetime.now().date()
            
            for record in records:
                if record.get('user_id') == user_id and record.get('estado') == 'activo':
                    # Verificar si aún está vigente
                    try:
                        fecha_fin = datetime.strptime(record.get('fecha_fin', ''), '%Y-%m-%d').date()
                        if fecha_fin >= today:
                            medicamentos_activos.append(record)
                    except:
                        # Si no hay fecha fin válida, asumir que está activo
                        medicamentos_activos.append(record)
            
            return medicamentos_activos
            
        except Exception as e:
            logger.error(f"Error obteniendo medicamentos: {e}")
            return []
    
    # CRUD Operations para Exámenes
    def create_examen(self, examen_data: Dict[str, Any]) -> str:
        """Registra un nuevo examen"""
        try:
            worksheet = self.get_worksheet('Examenes')
            
            # Generar ID único
            examen_id = f"EXM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            row_data = [
                examen_id,
                examen_data.get('user_id', ''),
                examen_data.get('atencion_id', ''),
                examen_data.get('tipo_examen', ''),
                examen_data.get('nombre_examen', ''),
                examen_data.get('fecha_solicitud', ''),
                examen_data.get('fecha_realizacion', ''),
                examen_data.get('resultado', ''),
                examen_data.get('archivo_url', ''),
                examen_data.get('observaciones', ''),
                'pendiente'
            ]
            
            worksheet.append_row(row_data)
            
            logger.info(f"Examen {examen_id} registrado exitosamente")
            return examen_id
            
        except Exception as e:
            logger.error(f"Error registrando examen: {e}")
            raise
    
    # Operaciones para Familiares
    def add_familiar_autorizado(self, familiar_data: Dict[str, Any]) -> str:
        """Agrega un familiar autorizado"""
        try:
            worksheet = self.get_worksheet('Familiares_Autorizados')
            
            # Generar ID único
            familiar_id = f"FAM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            row_data = [
                familiar_id,
                familiar_data.get('user_id', ''),
                familiar_data.get('nombre_familiar', ''),
                familiar_data.get('parentesco', ''),
                familiar_data.get('telefono', ''),
                familiar_data.get('email', ''),
                familiar_data.get('telegram_id', ''),
                familiar_data.get('permisos', 'lectura'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'activo',
                familiar_data.get('notificaciones', 'true')
            ]
            
            worksheet.append_row(row_data)
            
            logger.info(f"Familiar {familiar_id} autorizado exitosamente")
            return familiar_id
            
        except Exception as e:
            logger.error(f"Error autorizando familiar: {e}")
            raise
    
    def get_familiares_autorizados(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtiene los familiares autorizados de un usuario"""
        try:
            worksheet = self.get_worksheet('Familiares_Autorizados')
            records = worksheet.get_all_records()
            
            familiares = [
                record for record in records 
                if record.get('user_id') == user_id and record.get('estado') == 'activo'
            ]
            
            return familiares
            
        except Exception as e:
            logger.error(f"Error obteniendo familiares: {e}")
            return []
    
    # Logging
    def log_action(self, user_id: str, action: str, detail: str, ip_address: str = "", result: str = "success"):
        """Registra una acción en el log"""
        try:
            worksheet = self.get_worksheet('Logs_Acceso')
            
            log_id = f"LOG_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            row_data = [
                log_id,
                user_id,
                action,
                detail,
                ip_address,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                result
            ]
            
            worksheet.append_row(row_data)
            
        except Exception as e:
            logger.error(f"Error registrando log: {e}")
    
    # Métodos de utilidad
    def get_user_summary(self, user_id: str) -> Dict[str, Any]:
        """Obtiene un resumen completo del usuario"""
        try:
            user = self.get_user_by_telegram_id(user_id)
            if not user:
                return {}
            
            atenciones = self.get_user_atenciones(user.get('user_id', ''))
            medicamentos = self.get_user_medicamentos_activos(user.get('user_id', ''))
            familiares = self.get_familiares_autorizados(user.get('user_id', ''))
            
            return {
                'usuario': user,
                'total_atenciones': len(atenciones),
                'atenciones_recientes': atenciones[:5],
                'medicamentos_activos': len(medicamentos),
                'medicamentos': medicamentos,
                'familiares_autorizados': len(familiares)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen del usuario: {e}")
            return {}

    # Métodos para gestión familiar avanzada
    def authorize_family_member(self, user_id: str, family_data: Dict[str, Any]) -> str:
        """Autoriza a un familiar con permisos específicos"""
        try:
            worksheet = self.get_worksheet('Familiares_Autorizados')
            
            # Generar ID único
            familiar_id = f"FAM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            row_data = [
                familiar_id,
                user_id,
                family_data.get('nombre_familiar', ''),
                family_data.get('parentesco', ''),
                family_data.get('telefono', ''),
                family_data.get('email', ''),
                                 family_data.get('telegram_id', ''),  # Nuevo campo para telegram_id del familiar
                 family_data.get('permisos', 'lectura'),  # lectura, escritura, admin
                 datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                 'activo',
                 family_data.get('notificaciones', 'true')  # Recibir notificaciones
            ]
            
            worksheet.append_row(row_data)
            
            logger.info(f"Familiar {familiar_id} autorizado exitosamente")
            return familiar_id
            
        except Exception as e:
            logger.error(f"Error autorizando familiar: {e}")
            raise

    def get_managed_users(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtiene usuarios que puede gestionar el usuario actual"""
        try:
            worksheet = self.get_worksheet('Familiares_Autorizados')
            records = worksheet.get_all_records()
            
            managed_users = []
            
            for record in records:
                if (record.get('telegram_id') == str(user_id) and 
                    record.get('estado') == 'activo' and
                    record.get('permisos') in ['escritura', 'admin']):
                    
                    # Obtener datos del usuario principal
                    main_user = self.get_user_by_id(record.get('user_id'))
                    if main_user:
                        managed_users.append({
                            'id': record.get('user_id'),
                            'nombre': main_user.get('nombre', ''),
                            'apellido': main_user.get('apellido', ''),
                            'parentesco': record.get('parentesco', ''),
                            'permisos': record.get('permisos', '')
                        })
            
            return managed_users
            
        except Exception as e:
            logger.error(f"Error obteniendo usuarios gestionados: {e}")
            return []

    def check_family_permission(self, user_id: str, target_user_id: str) -> bool:
        """Verifica si un usuario tiene permisos para gestionar otro usuario"""
        try:
            # Un usuario siempre puede gestionar su propia información
            if user_id == target_user_id:
                return True
                
            worksheet = self.get_worksheet('Familiares_Autorizados')
            records = worksheet.get_all_records()
            
            for record in records:
                if (record.get('user_id') == target_user_id and 
                    record.get('telegram_id') == str(user_id) and
                    record.get('estado') == 'activo'):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verificando permisos familiares: {e}")
            return False

    def get_family_for_notifications(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtiene familiares que deben recibir notificaciones"""
        try:
            worksheet = self.get_worksheet('Familiares_Autorizados')
            records = worksheet.get_all_records()
            
            family_for_notifications = []
            
            for record in records:
                if (record.get('user_id') == user_id and 
                    record.get('estado') == 'activo' and
                    record.get('notificaciones') == 'true' and
                    record.get('telegram_id')):
                    
                    family_for_notifications.append({
                        'telegram_id': record.get('telegram_id'),
                        'nombre_familiar': record.get('nombre_familiar'),
                        'parentesco': record.get('parentesco')
                    })
            
            return family_for_notifications
            
        except Exception as e:
            logger.error(f"Error obteniendo familia para notificaciones: {e}")
            return []

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Busca un usuario por su ID interno"""
        try:
            worksheet = self.get_worksheet('Usuarios')
            records = worksheet.get_all_records()
            
            for record in records:
                if (record.get('id') == user_id or 
                    record.get('user_id') == user_id):
                    return record
            
            return None
            
        except Exception as e:
            logger.error(f"Error buscando usuario por ID: {e}")
            return None

    def get_medical_summary(self, user_id: str) -> Dict[str, Any]:
        """Obtiene resumen médico completo de un usuario"""
        try:
            atenciones = self.get_user_atenciones(user_id)
            medicamentos = self.get_user_medicamentos_activos(user_id)
            examenes = self.get_user_examenes(user_id)
            
            return {
                'total_consultas': len(atenciones),
                'consultas_recientes': atenciones[:3],
                'medicamentos_activos': len(medicamentos),
                'medicamentos': medicamentos,
                'total_examenes': len(examenes),
                'examenes_recientes': examenes[:3]
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen médico: {e}")
            return {}

    def get_user_examenes(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtiene exámenes de un usuario"""
        try:
            worksheet = self.get_worksheet('Examenes')
            records = worksheet.get_all_records()
            
            user_examenes = [
                record for record in records 
                if record.get('user_id') == user_id
            ]
            
            # Ordenar por fecha más reciente
            user_examenes.sort(
                key=lambda x: datetime.strptime(x.get('fecha_realizacion', '1900-01-01'), '%Y-%m-%d') if x.get('fecha_realizacion') else datetime.min,
                reverse=True
            )
            
            return user_examenes
            
        except Exception as e:
            logger.error(f"Error obteniendo exámenes: {e}")
            return []

    # Gestión de recordatorios y notificaciones
    def create_reminder(self, reminder_data: Dict[str, Any]) -> str:
        """Crea un recordatorio/notificación"""
        try:
            worksheet = self.get_worksheet('Recordatorios')
            
            # Generar ID único
            reminder_id = f"REM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            row_data = [
                reminder_id,
                reminder_data.get('user_id', ''),
                reminder_data.get('tipo', ''),  # medicamento, cita, general
                reminder_data.get('titulo', ''),
                reminder_data.get('mensaje', ''),
                reminder_data.get('fecha_programada', ''),
                reminder_data.get('hora_programada', ''),
                reminder_data.get('frecuencia', 'unica'),  # unica, diaria, semanal
                reminder_data.get('notificar_familiares', 'false'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'activo'
            ]
            
            worksheet.append_row(row_data)
            
            logger.info(f"Recordatorio {reminder_id} creado exitosamente")
            return reminder_id
            
        except Exception as e:
            logger.error(f"Error creando recordatorio: {e}")
            raise

    def get_user_active_reminders(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtiene recordatorios activos de un usuario"""
        try:
            worksheet = self.get_worksheet('Recordatorios')
            records = worksheet.get_all_records()
            
            active_reminders = []
            today = datetime.now().date()
            
            for record in records:
                if (record.get('user_id') == user_id and 
                    record.get('estado') == 'activo'):
                    
                    # Verificar si el recordatorio aún está vigente
                    try:
                        fecha_programada = datetime.strptime(record.get('fecha_programada', ''), '%Y-%m-%d').date()
                        if fecha_programada >= today:
                            active_reminders.append(record)
                    except:
                        # Si no hay fecha válida, incluir el recordatorio
                        active_reminders.append(record)
            
            return active_reminders
            
        except Exception as e:
            logger.error(f"Error obteniendo recordatorios activos: {e}")
            return []

    def update_sheet_headers(self, sheet_name: str, additional_headers: List[str]):
        """Actualiza headers de una hoja agregando campos faltantes"""
        try:
            worksheet = self.get_worksheet(sheet_name)
            current_headers = worksheet.row_values(1)
            
            new_headers = []
            for header in additional_headers:
                if header not in current_headers:
                    new_headers.append(header)
            
            if new_headers:
                # Agregar nuevos headers
                updated_headers = current_headers + new_headers
                worksheet.clear()
                worksheet.append_row(updated_headers)
                logger.info(f"Headers actualizados en {sheet_name}: {new_headers}")
            
        except Exception as e:
            logger.error(f"Error actualizando headers de {sheet_name}: {e}")

# Instancia global del gestor
sheets_db = SheetsManager() 