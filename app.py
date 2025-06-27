# MedConnect - Aplicación Principal Flask
# Backend para plataforma de gestión médica con Google Sheets y Telegram Bot

import os
import logging
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, make_response, send_from_directory
from flask_cors import CORS
import requests
import json
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from config import get_config, SHEETS_CONFIG
from auth_manager import AuthManager
from werkzeug.utils import secure_filename
import uuid

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)
config = get_config()
app.config.from_object(config)

# Configurar CORS
CORS(app, origins=config.CORS_ORIGINS)

# Configuración para subida de archivos
UPLOAD_FOLDER = 'static/uploads/medical_files'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'dcm', 'dicom'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Crear directorio de uploads si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configuración de Google Sheets
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_google_sheets_client():
    """Inicializa el cliente de Google Sheets"""
    try:
        if os.path.exists(app.config['GOOGLE_SERVICE_ACCOUNT_FILE']):
            creds = Credentials.from_service_account_file(
                app.config['GOOGLE_SERVICE_ACCOUNT_FILE'], 
                scopes=SCOPES
            )
        else:
            # Para Railway, usar variables de entorno
            service_account_info = json.loads(os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON', '{}'))
            creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
        
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        logger.error(f"Error inicializando Google Sheets: {e}")
        return None

# Cliente global de Google Sheets
sheets_client = get_google_sheets_client()

# Inicializar AuthManager
try:
    auth_manager = AuthManager()
    logger.info("✅ AuthManager inicializado correctamente")
except Exception as e:
    logger.error(f"❌ Error inicializando AuthManager: {e}")
    auth_manager = None

def get_spreadsheet():
    """Obtiene la hoja de cálculo principal"""
    if sheets_client:
        try:
            return sheets_client.open_by_key(app.config['GOOGLE_SHEETS_ID'])
        except Exception as e:
            logger.error(f"Error abriendo spreadsheet: {e}")
    return None

def get_current_user():
    """Obtiene los datos del usuario actual desde la sesión"""
    return session.get('user_data', {})

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(filename):
    """Genera un nombre único para el archivo"""
    ext = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    return unique_filename

# Hacer la función disponible en todas las plantillas
@app.context_processor
def inject_user():
    """Inyecta los datos del usuario en todas las plantillas"""
    return dict(current_user=get_current_user())

# Decorador para rutas que requieren autenticación
def login_required(f):
    """Decorador para rutas que requieren login"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Rutas de autenticación
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro de usuarios"""
    if not auth_manager:
        flash('Sistema de autenticación no disponible', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            user_data = {
                'email': request.form.get('email', '').strip().lower(),
                'password': request.form.get('password', ''),
                'nombre': request.form.get('nombre', '').strip(),
                'apellido': request.form.get('apellido', '').strip(),
                'telefono': request.form.get('telefono', '').strip(),
                'fecha_nacimiento': request.form.get('fecha_nacimiento', ''),
                'genero': request.form.get('genero', ''),
                'direccion': request.form.get('direccion', '').strip(),
                'ciudad': request.form.get('ciudad', '').strip(),
                'tipo_usuario': request.form.get('tipo_usuario', '').strip()
            }
            
            # Validar confirmación de contraseña
            confirm_password = request.form.get('confirm_password', '')
            if user_data['password'] != confirm_password:
                return render_template('register.html', 
                                     message='Las contraseñas no coinciden', 
                                     success=False)
            
            # Registrar usuario
            success, message = auth_manager.register_user(user_data)
            
            if success:
                logger.info(f"✅ Usuario registrado exitosamente: {user_data['email']}")
                return render_template('register.html', 
                                     message=message, 
                                     success=True)
            else:
                return render_template('register.html', 
                                     message=message, 
                                     success=False)
                
        except Exception as e:
            logger.error(f"❌ Error en registro: {e}")
            return render_template('register.html', 
                                 message='Error interno del servidor', 
                                 success=False)
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión"""
    if not auth_manager:
        flash('Sistema de autenticación no disponible', 'error')
        return redirect(url_for('index'))
    
    # Si ya está logueado, redirigir al dashboard
    if 'user_id' in session:
        user_type = session.get('user_type', 'paciente')
        if user_type == 'profesional':
            return redirect(url_for('professional_dashboard'))
        else:
            return redirect(url_for('patient_dashboard'))
    
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            
            if not email or not password:
                return render_template('login.html', 
                                     message='Email y contraseña son requeridos', 
                                     success=False)
            
            # Intentar login
            success, message, user_data = auth_manager.login_user(email, password)
            
            if success and user_data:
                # Crear sesión con información completa del usuario
                session['user_id'] = user_data['id']
                session['user_email'] = user_data['email']
                session['user_name'] = f"{user_data['nombre']} {user_data['apellido']}"
                session['user_type'] = user_data['tipo_usuario']
                session['user_data'] = user_data
                session['just_logged_in'] = True  # Flag para mostrar mensaje de bienvenida
                
                logger.info(f"✅ Login exitoso: {email}")
                
                # Redirigir según tipo de usuario
                if user_data['tipo_usuario'] == 'profesional':
                    return redirect(url_for('professional_dashboard'))
                else:
                    return redirect(url_for('patient_dashboard'))
            else:
                return render_template('login.html', 
                                     message=message, 
                                     success=False)
                
        except Exception as e:
            logger.error(f"❌ Error en login: {e}")
            return render_template('login.html', 
                                 message='Error interno del servidor', 
                                 success=False)
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    try:
        user_email = session.get('user_email', 'Usuario')
        logger.info(f"🔄 Iniciando logout para: {user_email}")
        
        # Limpiar sesión completamente múltiples veces
        session.clear()
        session.permanent = False
        
        # Forzar eliminación de claves específicas
        for key in ['user_id', 'user_email', 'user_name', 'user_type', 'user_data']:
            session.pop(key, None)
        
        logger.info(f"✅ Sesión limpiada completamente para: {user_email}")
        logger.info(f"🔍 Sesión después del clear: {dict(session)}")
        
        # NO usar flash ya que requiere sesión
        # En su lugar, usar parámetro URL
        
        # Crear respuesta con headers anti-cache muy fuertes
        response = make_response(redirect('/?logout=success'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        response.headers['Clear-Site-Data'] = '"cache", "cookies", "storage"'
        
        # Eliminar cookies de sesión explícitamente
        response.set_cookie('session', '', expires=0)
        response.set_cookie('session', '', expires=0, domain='.medconnect.cl')
        response.set_cookie('session', '', expires=0, path='/')
        
        logger.info("🔄 Redirigiendo a página principal con headers anti-cache...")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error en logout: {e}")
        # En caso de error, limpiar toda la sesión y redirigir
        try:
            session.clear()
            session.permanent = False
            logger.info("✅ Sesión limpiada después del error")
        except Exception as clear_error:
            logger.error(f"❌ Error limpiando sesión: {clear_error}")
        
        # Respuesta de error también con headers anti-cache
        response = make_response(redirect('/?logout=error'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'  
        response.headers['Expires'] = '-1'
        
        logger.info("🔄 Redirigiendo a página principal después del error...")
        return response

# Rutas principales del frontend
@app.route('/')
def index():
    """Página principal - Landing page"""
    try:
        # Verificar si venimos de un logout
        logout_param = request.args.get('logout')
        if logout_param in ['success', 'error']:
            logger.info(f"🔄 Detectado logout: {logout_param} - Forzando limpieza de sesión")
            # Forzar limpieza total de sesión
            session.clear()
            session.permanent = False
            for key in ['user_id', 'user_email', 'user_name', 'user_type', 'user_data']:
                session.pop(key, None)
            
            # Forzar variables a None
            user_id = None
            user_name = None
            user_type = None
            
            logger.info("🔄 Sesión forzada a None después de logout")
        else:
            # Obtener datos de sesión de forma segura
            user_id = session.get('user_id')
            user_name = session.get('user_name')
            user_type = session.get('user_type')
        
        # Log para debugging
        logger.info(f"🔍 Index - user_id: {user_id}, user_name: {user_name}, user_type: {user_type}")
        logger.info(f"🔍 Sesión completa: {dict(session)}")
        
        # Crear respuesta sin cache con headers muy fuertes
        response = make_response(render_template('index.html', 
                                               user_id=user_id,
                                               user_name=user_name, 
                                               user_type=user_type,
                                               logout_message=logout_param))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        response.headers['Last-Modified'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # Si venimos de logout, eliminar cookies adicionales
        if logout_param:
            response.set_cookie('session', '', expires=0)
            response.set_cookie('session', '', expires=0, domain='.medconnect.cl')
            response.set_cookie('session', '', expires=0, path='/')
        
        return response
    except Exception as e:
        logger.error(f"Error en index: {e}")
        return render_template('index.html', user_id=None, user_name=None, user_type=None)

@app.route('/patient')
@login_required
def patient_dashboard():
    """Dashboard para pacientes"""
    try:
        user_data = session.get('user_data', {})
        just_logged_in = session.pop('just_logged_in', False)  # Obtener y remover el flag
        
        # Log para debugging
        if just_logged_in:
            logger.info(f"🎉 Mostrando mensaje de bienvenida para paciente: {user_data.get('nombre', 'Usuario')}")
        
        return render_template('patient.html', 
                             user=user_data, 
                             just_logged_in=just_logged_in)
    except Exception as e:
        logger.error(f"Error en dashboard paciente: {e}")
        return render_template('patient.html', user={}, just_logged_in=False)

@app.route('/professional')
@login_required
def professional_dashboard():
    """Dashboard para profesionales"""
    try:
        user_data = session.get('user_data', {})
        just_logged_in = session.pop('just_logged_in', False)  # Obtener y remover el flag
        
        # Log para debugging
        if just_logged_in:
            logger.info(f"🎉 Mostrando mensaje de bienvenida para profesional: {user_data.get('nombre', 'Usuario')}")
        
        return render_template('professional.html', 
                             user=user_data, 
                             just_logged_in=just_logged_in)
    except Exception as e:
        logger.error(f"Error en dashboard profesional: {e}")
        return render_template('professional.html', user={}, just_logged_in=False)

@app.route('/profile')
@login_required
def profile():
    """Página de perfil de usuario"""
    logger.info("🔍 INICIANDO función profile()")
    try:
        user_data = session.get('user_data', {})
        logger.info(f"🔍 Datos del usuario en perfil: {user_data}")
        logger.info(f"🔍 Sesión completa: {dict(session)}")
        
        # Crear respuesta sin cache
        response = make_response(render_template('profile.html', user=user_data))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
    except Exception as e:
        logger.error(f"❌ Error en perfil: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return render_template('profile.html', user={})

@app.route('/services')
@login_required
def services():
    """Página de servicios del profesional"""
    if session.get('user_type') != 'profesional':
        flash('Acceso denegado: Solo para profesionales médicos', 'error')
        return redirect(url_for('index'))
    
    user_data = session.get('user_data', {})
    return render_template('services.html', user=user_data)

@app.route('/requests')
@login_required
def requests():
    """Página de solicitudes del profesional"""
    if session.get('user_type') != 'profesional':
        flash('Acceso denegado: Solo para profesionales médicos', 'error')
        return redirect(url_for('index'))
    
    user_data = session.get('user_data', {})
    return render_template('requests.html', user=user_data)



@app.route('/chat')
@login_required
def chat():
    """Página de chat del profesional"""
    if session.get('user_type') != 'profesional':
        flash('Acceso denegado: Solo para profesionales médicos', 'error')
        return redirect(url_for('index'))
    
    user_data = session.get('user_data', {})
    return render_template('chat.html', user=user_data)

# API Routes para el frontend
@app.route('/api/patient/<patient_id>/consultations')
def get_patient_consultations(patient_id):
    """Obtiene las consultas de un paciente"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        # Leer datos de la hoja Consultas manualmente para evitar errores de headers
        try:
            worksheet = spreadsheet.worksheet('Consultas')
            all_values = worksheet.get_all_values()
            
            consultations = []
            
            if len(all_values) > 1:
                headers = all_values[0]
                logger.info(f"📋 Headers de Consultas: {headers}")
                
                # Headers reales: ['id', 'patient_id', 'doctor', 'specialty', 'date', 'diagnosis', 'treatment', 'notes', 'status']
                for row in all_values[1:]:
                    if len(row) >= len(headers) and any(cell.strip() for cell in row):
                        # Verificar si pertenece al paciente
                        patient_id_cell = row[1] if len(row) > 1 else ''
                        
                        if str(patient_id_cell) == str(patient_id):
                            # Transformar al formato esperado por la plataforma web
                            consultation_formatted = {
                                'id': row[0] if len(row) > 0 else '',  # id
                                'patient_id': patient_id,
                                'doctor': row[2] if len(row) > 2 else '',  # doctor
                                'specialty': row[3] if len(row) > 3 else '',  # specialty
                                'date': convert_date_format(row[4] if len(row) > 4 else ''),  # date
                                'diagnosis': row[5] if len(row) > 5 else '',  # diagnosis
                                'treatment': row[6] if len(row) > 6 else '',  # treatment
                                'notes': row[7] if len(row) > 7 else '',  # notes
                                'status': row[8] if len(row) > 8 else 'completada'  # status
                            }
                            
                            consultations.append(consultation_formatted)
            
            logger.info(f"🔍 Consultas encontradas para paciente {patient_id}: {len(consultations)}")
            
            return jsonify({'consultations': consultations})
            
        except gspread.WorksheetNotFound:
            logger.warning("📝 Hoja 'Consultas' no encontrada")
            return jsonify({'consultations': []})
            
    except Exception as e:
        logger.error(f"Error obteniendo consultas: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/patient/<patient_id>/medications')
def get_patient_medications(patient_id):
    """Obtiene los medicamentos de un paciente"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        # Leer datos de la hoja Medicamentos manualmente para evitar errores de headers
        try:
            worksheet = spreadsheet.worksheet('Medicamentos')
            all_values = worksheet.get_all_values()
            
            medications = []
            
            if len(all_values) > 1:
                headers = all_values[0]
                logger.info(f"📋 Headers de Medicamentos: {headers}")
                
                # Headers reales: ['id', 'patient_id', 'medication', 'dosage', 'frequency', 'start_date', 'end_date', 'prescribed_by', 'status']
                for row in all_values[1:]:
                    if len(row) >= len(headers) and any(cell.strip() for cell in row):
                        # Verificar si pertenece al paciente
                        patient_id_cell = row[1] if len(row) > 1 else ''
                        
                        if str(patient_id_cell) == str(patient_id):
                            # Transformar al formato esperado por la plataforma web
                            medication_formatted = {
                                'id': row[0] if len(row) > 0 else '',  # id
                                'patient_id': patient_id,
                                'name': row[2] if len(row) > 2 else '',  # medication
                                'dosage': row[3] if len(row) > 3 else '',  # dosage
                                'frequency': row[4] if len(row) > 4 else '',  # frequency
                                'prescribing_doctor': row[7] if len(row) > 7 else '',  # prescribed_by
                                'start_date': convert_date_format(row[5] if len(row) > 5 else ''),  # start_date
                                'end_date': convert_date_format(row[6] if len(row) > 6 else ''),  # end_date
                                'instructions': '',  # No disponible en la estructura actual
                                'status': row[8] if len(row) > 8 else 'activo'  # status
                            }
                            
                            medications.append(medication_formatted)
            
            logger.info(f"🔍 Medicamentos encontrados para paciente {patient_id}: {len(medications)}")
            
            return jsonify({'medications': medications})
            
        except gspread.WorksheetNotFound:
            logger.warning("📝 Hoja 'Medicamentos' no encontrada")
            return jsonify({'medications': []})
            
    except Exception as e:
        logger.error(f"Error obteniendo medicamentos: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/patient/<patient_id>/exams')
def get_patient_exams(patient_id):
    """Obtiene los exámenes de un paciente"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        # Leer datos de la hoja 'Examenes' (nueva estructura)
        try:
            examenes_worksheet = spreadsheet.worksheet('Examenes')
            all_exam_values = examenes_worksheet.get_all_values()
            
            patient_exams = []
            
            if len(all_exam_values) > 1:
                headers = all_exam_values[0]
                logger.info(f"📋 Headers de Examenes: {headers}")
                
                # Headers reales: ['id', 'patient_id', 'exam_type', 'date', 'results', 'lab', 'doctor', 'file_url', 'status']
                for row in all_exam_values[1:]:
                    if len(row) >= len(headers) and any(cell.strip() for cell in row):
                        # Verificar si pertenece al paciente
                        patient_id_cell = row[1] if len(row) > 1 else ''
                        
                        if str(patient_id_cell) == str(patient_id):
                            # Transformar al formato esperado por la plataforma web
                            original_date = row[3] if len(row) > 3 else ''
                            converted_date = convert_date_format(original_date)
                            logger.info(f"📅 Fecha original: '{original_date}' → Convertida: '{converted_date}'")
                            
                            exam_formatted = {
                                'id': row[0] if len(row) > 0 else '',  # id
                                'patient_id': patient_id,
                                'exam_type': row[2] if len(row) > 2 else '',  # exam_type
                                'date': converted_date,  # date
                                'results': row[4] if len(row) > 4 else '',  # results
                                'lab': row[5] if len(row) > 5 else '',  # lab
                                'doctor': row[6] if len(row) > 6 else '',  # doctor
                                'file_url': row[7] if len(row) > 7 else '',  # file_url
                                'status': row[8] if len(row) > 8 else 'completado'  # status
                            }
                            
                            patient_exams.append(exam_formatted)
            
            logger.info(f"🔍 Exámenes encontrados para paciente {patient_id}: {len(patient_exams)}")
            
            if patient_exams:
                return jsonify({'exams': patient_exams})
                
        except gspread.WorksheetNotFound:
            logger.info("📝 Hoja 'Examenes' no encontrada, intentando con estructura antigua")
        
        # Si no hay resultados en la nueva hoja, probar con la hoja antigua
        try:
            worksheet = spreadsheet.worksheet(SHEETS_CONFIG['exams']['name'])
            
            # Obtener datos usando la estructura antigua como respaldo
            all_records = worksheet.get_all_records()
            
            patient_exams = []
            for record in all_records:
                if str(record.get('patient_id', '')) == str(patient_id):
                    original_date = record.get('date', '')
                    converted_date = convert_date_format(original_date)
                    logger.info(f"📅 Fecha original (antigua): '{original_date}' → Convertida: '{converted_date}'")
                    
                    exam_formatted = {
                        'id': record.get('id', ''),
                        'patient_id': record.get('patient_id', ''),
                        'exam_type': record.get('exam_type', ''),
                        'date': converted_date,
                        'results': record.get('results', ''),
                        'lab': record.get('lab', ''),
                        'doctor': record.get('doctor', ''),
                        'file_url': record.get('file_url', ''),
                        'status': record.get('status', 'completado')
                    }
                    patient_exams.append(exam_formatted)
            
            logger.info(f"🔍 Exámenes encontrados en estructura antigua para paciente {patient_id}: {len(patient_exams)}")
            
            return jsonify({'exams': patient_exams})
            
        except gspread.WorksheetNotFound:
            logger.warning("📝 Ninguna hoja de exámenes encontrada")
            return jsonify({'exams': []})
            
    except Exception as e:
        logger.error(f"Error obteniendo exámenes: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/patient/<patient_id>/family')
def get_patient_family(patient_id):
    """Obtiene los familiares de un paciente"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        worksheet = spreadsheet.worksheet(SHEETS_CONFIG['family_members']['name'])
        records = worksheet.get_all_records()
        
        # Filtrar por patient_id
        patient_family = [r for r in records if str(r.get('patient_id')) == str(patient_id)]
        
        logger.info(f"🔍 Familiares encontrados para paciente {patient_id}: {len(patient_family)}")
        
        return jsonify({'family': patient_family})
    except Exception as e:
        logger.error(f"Error obteniendo familiares: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# APIs para eliminar datos
@app.route('/api/patient/<patient_id>/consultations/<consultation_id>', methods=['DELETE'])
@login_required
def delete_consultation(patient_id, consultation_id):
    """Elimina una consulta médica"""
    try:
        # Verificar que el usuario solo pueda eliminar sus propios datos
        if str(session.get('user_id')) != str(patient_id):
            return jsonify({'error': 'No autorizado'}), 403
        
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        # Usar la hoja 'Consultas' que existe realmente
        try:
            worksheet = spreadsheet.worksheet('Consultas')
            all_values = worksheet.get_all_values()
            
            # Buscar la fila a eliminar
            row_to_delete = None
            if len(all_values) > 1:
                for i, row in enumerate(all_values[1:], start=2):  # Start from row 2 (after headers)
                    if len(row) > 1 and str(row[0]) == str(consultation_id) and str(row[1]) == str(patient_id):
                        row_to_delete = i
                        break
            
            if row_to_delete:
                worksheet.delete_rows(row_to_delete)
                logger.info(f"✅ Consulta {consultation_id} eliminada para paciente {patient_id}")
                return jsonify({'success': True, 'message': 'Consulta eliminada exitosamente'})
            else:
                return jsonify({'error': 'Consulta no encontrada'}), 404
                
        except gspread.WorksheetNotFound:
            return jsonify({'error': 'Hoja de consultas no encontrada'}), 404
            
    except Exception as e:
        logger.error(f"Error eliminando consulta: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/patient/<patient_id>/medications/<medication_id>', methods=['DELETE'])
@login_required
def delete_medication(patient_id, medication_id):
    """Elimina un medicamento"""
    try:
        # Verificar que el usuario solo pueda eliminar sus propios datos
        if str(session.get('user_id')) != str(patient_id):
            return jsonify({'error': 'No autorizado'}), 403
        
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        # Usar la hoja 'Medicamentos' que existe realmente
        try:
            worksheet = spreadsheet.worksheet('Medicamentos')
            all_values = worksheet.get_all_values()
            
            # Buscar la fila a eliminar
            row_to_delete = None
            if len(all_values) > 1:
                for i, row in enumerate(all_values[1:], start=2):  # Start from row 2 (after headers)
                    if len(row) > 1 and str(row[0]) == str(medication_id) and str(row[1]) == str(patient_id):
                        row_to_delete = i
                        break
            
            if row_to_delete:
                worksheet.delete_rows(row_to_delete)
                logger.info(f"✅ Medicamento {medication_id} eliminado para paciente {patient_id}")
                return jsonify({'success': True, 'message': 'Medicamento eliminado exitosamente'})
            else:
                return jsonify({'error': 'Medicamento no encontrado'}), 404
                
        except gspread.WorksheetNotFound:
            return jsonify({'error': 'Hoja de medicamentos no encontrada'}), 404
            
    except Exception as e:
        logger.error(f"Error eliminando medicamento: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/patient/<patient_id>/exams/<exam_id>', methods=['DELETE'])
@login_required
def delete_exam(patient_id, exam_id):
    """Elimina un examen"""
    try:
        # Verificar que el usuario solo pueda eliminar sus propios datos
        if str(session.get('user_id')) != str(patient_id):
            return jsonify({'error': 'No autorizado'}), 403
        
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        # Usar la hoja 'Examenes' que existe realmente
        try:
            worksheet = spreadsheet.worksheet('Examenes')
            all_values = worksheet.get_all_values()
            
            # Buscar la fila a eliminar
            row_to_delete = None
            if len(all_values) > 1:
                for i, row in enumerate(all_values[1:], start=2):  # Start from row 2 (after headers)
                    if len(row) > 1 and str(row[0]) == str(exam_id) and str(row[1]) == str(patient_id):
                        row_to_delete = i
                        break
            
            if row_to_delete:
                worksheet.delete_rows(row_to_delete)
                logger.info(f"✅ Examen {exam_id} eliminado para paciente {patient_id}")
                return jsonify({'success': True, 'message': 'Examen eliminado exitosamente'})
            else:
                return jsonify({'error': 'Examen no encontrado'}), 404
                
        except gspread.WorksheetNotFound:
            return jsonify({'error': 'Hoja de exámenes no encontrada'}), 404
            
    except Exception as e:
        logger.error(f"Error eliminando examen: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/patient/<patient_id>/family/<family_id>', methods=['DELETE'])
@login_required
def delete_family_member(patient_id, family_id):
    """Elimina un familiar"""
    try:
        # Verificar que el usuario solo pueda eliminar sus propios datos
        if str(session.get('user_id')) != str(patient_id):
            return jsonify({'error': 'No autorizado'}), 403
        
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        worksheet = spreadsheet.worksheet(SHEETS_CONFIG['family_members']['name'])
        records = worksheet.get_all_records()
        
        # Buscar la fila a eliminar
        row_to_delete = None
        for i, record in enumerate(records, start=2):  # Start from row 2 (after headers)
            if str(record.get('id')) == str(family_id) and str(record.get('patient_id')) == str(patient_id):
                row_to_delete = i
                break
        
        if row_to_delete:
            worksheet.delete_rows(row_to_delete)
            logger.info(f"✅ Familiar {family_id} eliminado para paciente {patient_id}")
            return jsonify({'success': True, 'message': 'Familiar eliminado exitosamente'})
        else:
            return jsonify({'error': 'Familiar no encontrado'}), 404
            
    except Exception as e:
        logger.error(f"Error eliminando familiar: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# APIs para actualizar información del perfil
@app.route('/api/profile/personal', methods=['PUT'])
@login_required
def update_personal_info():
    """Actualiza la información personal del usuario"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Usuario no autenticado'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        # Validar campos requeridos
        required_fields = ['nombre', 'apellido', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'El campo {field} es requerido'}), 400
        
        # Validar formato de email
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return jsonify({'error': 'Formato de email inválido'}), 400
        
        # Validar teléfono si se proporciona
        if data.get('telefono'):
            try:
                telefono = int(data['telefono'])
                if telefono <= 0:
                    return jsonify({'error': 'Teléfono debe ser un número positivo'}), 400
            except ValueError:
                return jsonify({'error': 'Teléfono debe ser un número válido'}), 400
        
        # Actualizar en Google Sheets
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        worksheet = spreadsheet.worksheet(SHEETS_CONFIG['users']['name'])
        records = worksheet.get_all_records()
        
        # Buscar el usuario
        user_row = None
        for i, record in enumerate(records, start=2):
            if record.get('id') == user_id:
                user_row = i
                break
        
        if not user_row:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Preparar datos para actualizar
        update_data = {
            'nombre': data['nombre'],
            'apellido': data['apellido'],
            'email': data['email'],
            'telefono': data.get('telefono', ''),
            'fecha_nacimiento': data.get('fecha_nacimiento', ''),
            'genero': data.get('genero', ''),
            'direccion': data.get('direccion', ''),
            'ciudad': data.get('ciudad', '')
        }
        
        # Actualizar fila en Google Sheets
        headers = worksheet.row_values(1)
        for field, value in update_data.items():
            if field in headers:
                col_index = headers.index(field) + 1
                worksheet.update_cell(user_row, col_index, value)
        
        # Actualizar sesión
        user_data = session.get('user_data', {})
        user_data.update(update_data)
        session['user_data'] = user_data
        session['user_email'] = data['email']
        session['user_name'] = f"{data['nombre']} {data['apellido']}"
        
        logger.info(f"✅ Información personal actualizada para usuario {user_id}")
        return jsonify({'success': True, 'message': 'Información personal actualizada exitosamente'})
        
    except Exception as e:
        logger.error(f"Error actualizando información personal: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/profile/medical', methods=['PUT'])
@login_required
def update_medical_info():
    """Actualiza la información médica del usuario"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Usuario no autenticado'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        # Por ahora, simular actualización exitosa
        # En una implementación real, aquí se actualizaría una tabla de información médica
        logger.info(f"✅ Información médica actualizada para usuario {user_id}")
        return jsonify({'success': True, 'message': 'Información médica actualizada exitosamente'})
        
    except Exception as e:
        logger.error(f"Error actualizando información médica: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/profile/notifications', methods=['PUT'])
@login_required
def update_notification_settings():
    """Actualiza las configuraciones de notificaciones"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Usuario no autenticado'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        # Por ahora, simular actualización exitosa
        # En una implementación real, aquí se guardarían las preferencias de notificación
        logger.info(f"✅ Configuraciones de notificación actualizadas para usuario {user_id}")
        return jsonify({'success': True, 'message': 'Configuraciones de notificación actualizadas exitosamente'})
        
    except Exception as e:
        logger.error(f"Error actualizando configuraciones de notificación: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# Webhook para Telegram Bot
@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    """Webhook para recibir mensajes del bot de Telegram"""
    try:
        data = request.get_json()
        logger.info(f"Webhook recibido: {data}")
        
        # Procesar mensaje del bot
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            user_id = message['from']['id']
            username = message['from'].get('username', 'Sin username')
            
            # Registrar interacción en Google Sheets
            log_bot_interaction(user_id, username, text, chat_id)
            
            # Procesar comando o mensaje
            response = process_telegram_message(text, chat_id, user_id)
            
            # Enviar respuesta
            if response:
                send_telegram_message(chat_id, response)
        
        return jsonify({'status': 'ok'})
    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        return jsonify({'error': 'Error procesando webhook'}), 500

def log_bot_interaction(user_id, username, message, chat_id):
    """Registra la interacción del bot en Google Sheets"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return
        
        worksheet = spreadsheet.worksheet(SHEETS_CONFIG['bot_interactions']['name'])
        
        # Preparar datos
        row_data = [
            len(worksheet.get_all_values()) + 1,  # ID auto-incrementado
            user_id,
            username,
            message,
            '',  # Response se llenará después
            datetime.now().isoformat(),
            'message',
            'processed'
        ]
        
        worksheet.append_row(row_data)
        logger.info(f"Interacción registrada para usuario {user_id}")
    except Exception as e:
        logger.error(f"Error registrando interacción: {e}")

def process_telegram_message(text, chat_id, user_id):
    """Procesa mensajes del bot de Telegram"""
    text = text.lower().strip()
    
    # Intentar obtener información del usuario registrado
    user_info = get_telegram_user_info(user_id)
    
    if text.startswith('/start'):
        if user_info:
            nombre = user_info.get('nombre', 'Usuario')
            apellido = user_info.get('apellido', '')
            return f"""¡Hola {nombre} {apellido}! 👋 

¡Qué bueno verte de nuevo en MedConnect! 🏥

Como usuario registrado, puedo ayudarte con:

📋 Registrar consultas médicas
💊 Gestionar medicamentos  
🩺 Registrar exámenes
👨‍👩‍👧‍👦 Notificar a familiares
📊 Consultar tu historial personalizado

¿En qué puedo ayudarte hoy?"""
        else:
            return """¡Hola! 👋 Bienvenido a MedConnect

Soy tu asistente personal de salud. 

📱 **¿Ya tienes cuenta en MedConnect?**
Si ya estás registrado en nuestra plataforma web, puedes vincular tu cuenta escribiendo:
`/vincular tu-email@ejemplo.com`

Si aún no tienes cuenta, visita: https://medconnect.cl/register

Una vez vinculada tu cuenta, podrás:
📋 Registrar consultas médicas
💊 Gestionar medicamentos  
🩺 Registrar exámenes
👨‍👩‍👧‍👦 Notificar a familiares
📊 Ver tu historial personalizado

¿En qué puedo ayudarte?"""
    
    elif text.startswith('/vincular'):
        return handle_account_linking(text, user_id)
    
    elif 'consulta' in text or 'médico' in text:
        if user_info:
            nombre = user_info.get('nombre', 'Usuario')
            return f"""📋 Perfecto {nombre}, para registrar una consulta médica necesito:

1. Fecha de la consulta
2. Nombre del médico
3. Especialidad
4. Diagnóstico
5. Tratamiento indicado

Esta información se guardará en tu historial personal. ¿Podrías proporcionarme estos datos?"""
        else:
            return """📋 Para registrar una consulta médica, necesito:

1. Fecha de la consulta
2. Nombre del médico
3. Especialidad
4. Diagnóstico
5. Tratamiento indicado

💡 **Tip:** Si vinculas tu cuenta de MedConnect con `/vincular tu-email@ejemplo.com`, podré guardar esta información en tu historial personal.

¿Podrías proporcionarme esta información?"""
    
    elif 'medicamento' in text or 'medicina' in text:
        if user_info:
            nombre = user_info.get('nombre', 'Usuario')
            return f"""💊 Hola {nombre}, para registrar un medicamento necesito:

1. Nombre del medicamento
2. Dosis (ej: 50mg)
3. Frecuencia (ej: cada 8 horas)
4. Médico que lo prescribió

Lo guardaré en tu perfil personalizado. ¿Podrías darme estos datos?"""
        else:
            return """💊 Para registrar un medicamento, necesito:

1. Nombre del medicamento
2. Dosis (ej: 50mg)
3. Frecuencia (ej: cada 8 horas)
4. Médico que lo prescribió

💡 **Tip:** Vincula tu cuenta con `/vincular tu-email@ejemplo.com` para un seguimiento personalizado.

¿Podrías darme estos datos?"""
    
    elif 'examen' in text or 'análisis' in text:
        if user_info:
            nombre = user_info.get('nombre', 'Usuario')
            return f"""🩺 Hola {nombre}, para registrar un examen necesito:

1. Tipo de examen
2. Fecha realizada
3. Laboratorio o centro médico
4. Resultados principales

Se agregará a tu historial médico. ¿Tienes esta información?"""
        else:
            return """🩺 Para registrar un examen, necesito:

1. Tipo de examen
2. Fecha realizada
3. Laboratorio o centro médico
4. Resultados principales

💡 **Tip:** Con tu cuenta vinculada, mantendré un historial completo de tus exámenes.

¿Tienes esta información?"""
    
    elif 'historial' in text or 'ver' in text:
        if user_info:
            nombre = user_info.get('nombre', 'Usuario')
            return f"""📊 Hola {nombre}, para ver tu historial completo personalizado, visita:
https://medconnect.cl/patient

En tu dashboard podrás ver:
✅ Todas tus consultas médicas
✅ Medicamentos actuales
✅ Resultados de exámenes
✅ Próximas citas

También puedes preguntarme directamente sobre:
- Últimas consultas
- Medicamentos activos
- Próximas citas

¿Qué te gustaría consultar?"""
        else:
            return f"""📊 Para ver tu historial médico completo, necesitas vincular tu cuenta primero.

**¿Ya tienes cuenta en MedConnect?**
Escribe: `/vincular tu-email@ejemplo.com`

**¿Aún no tienes cuenta?**
Regístrate en: https://medconnect.cl/register

Una vez vinculada, podrás ver toda tu información médica personalizada.

¿Te gustaría que te ayude con algo más?"""
    
    else:
        if user_info:
            nombre = user_info.get('nombre', 'Usuario')
            return f"""Hola {nombre}, no estoy seguro de cómo ayudarte con eso. 

Puedes preguntarme sobre:
📋 Registrar consultas médicas
💊 Gestionar medicamentos
🩺 Registrar exámenes
📊 Ver tu historial

O escribe /start para ver todas las opciones."""
        else:
            return """No estoy seguro de cómo ayudarte con eso. 

Puedes preguntarme sobre:
📋 Registrar consultas médicas
💊 Gestionar medicamentos
🩺 Registrar exámenes
📊 Ver tu historial

💡 **Tip:** Vincula tu cuenta con `/vincular tu-email@ejemplo.com` para una experiencia personalizada.

O escribe /start para ver todas las opciones."""

def get_telegram_user_info(telegram_user_id):
    """Obtiene información del usuario registrado por su ID de Telegram"""
    try:
        if not auth_manager:
            return None
            
        user_info = auth_manager.get_user_by_telegram_id(telegram_user_id)
        return user_info
    except Exception as e:
        logger.error(f"Error obteniendo info de usuario Telegram {telegram_user_id}: {e}")
        return None

def handle_account_linking(text, telegram_user_id):
    """Maneja la vinculación de cuenta de Telegram"""
    try:
        parts = text.split()
        if len(parts) < 2:
            return """❌ Formato incorrecto. 

**Uso correcto:**
`/vincular tu-email@ejemplo.com`

**Ejemplo:**
`/vincular maria.gonzalez@gmail.com`

Asegúrate de usar el mismo email con el que te registraste en MedConnect."""
        
        email = parts[1].strip()
        
        # Validar formato de email básico
        if '@' not in email or '.' not in email:
            return """❌ El email no parece válido.

**Formato esperado:**
`/vincular tu-email@ejemplo.com`

Por favor verifica e intenta de nuevo."""
        
        if not auth_manager:
            return "❌ Sistema de autenticación no disponible temporalmente. Intenta más tarde."
        
        # Verificar si el usuario existe
        user_data = auth_manager.get_user_by_email(email)
        if not user_data:
            return f"""❌ No encontré ninguna cuenta con el email: `{email}`

**¿Posibles soluciones:**
1. Verifica que escribiste correctamente tu email
2. Si aún no tienes cuenta, regístrate en: https://medconnect.cl/register
3. Intenta de nuevo: `/vincular tu-email-correcto@ejemplo.com`"""
        
        # Intentar vincular la cuenta
        success, message, user_info = auth_manager.link_telegram_account(email, telegram_user_id)
        
        if success and user_info:
            nombre = user_info.get('nombre', 'Usuario')
            apellido = user_info.get('apellido', '')
            return f"""✅ ¡Cuenta vinculada exitosamente!

¡Hola {nombre} {apellido}! 🎉

Tu cuenta de Telegram ahora está conectada con MedConnect. A partir de ahora:

✨ **Experiencia personalizada**
📋 Historial médico completo
💊 Seguimiento de medicamentos
🩺 Registro de exámenes
👨‍👩‍👧‍👦 Notificaciones familiares

Escribe `/start` para comenzar con tu experiencia personalizada."""
        else:
            return f"""❌ {message}

**Si el problema persiste:**
1. Verifica tu email: `{email}`
2. Contacta soporte si necesitas ayuda
3. O intenta registrarte en: https://medconnect.cl/register"""
            
    except Exception as e:
        logger.error(f"Error en vinculación de cuenta: {e}")
        return """❌ Error interno al vincular cuenta.

Por favor intenta de nuevo en unos minutos o contacta soporte."""

def send_telegram_message(telegram_id, message):
    """Envía un mensaje a través del bot de Telegram"""
    try:
        # Token del bot
        BOT_TOKEN = "7618933472:AAEYCYi9Sso9YVP9aB8dLWvlZ-1hxqgdhck"  # Token correcto del bot
        
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': str(telegram_id),  # Asegurar que sea string
            'text': message,
            'parse_mode': 'HTML'
        }
        
        import requests  # Asegurar import local
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"✅ Mensaje enviado a Telegram ID: {telegram_id}")
            return True
        else:
            logger.error(f"❌ Error enviando mensaje a Telegram: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error enviando mensaje de Telegram: {e}")
        return False

# Configurar webhook del bot
@app.route('/setup-webhook')
def setup_webhook():
    """Configura el webhook del bot de Telegram"""
    try:
        url = f"https://api.telegram.org/bot{app.config['TELEGRAM_BOT_TOKEN']}/setWebhook"
        data = {
            'url': app.config['TELEGRAM_WEBHOOK_URL']
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        return jsonify({
            'status': 'success',
            'webhook_url': app.config['TELEGRAM_WEBHOOK_URL'],
            'response': response.json()
        })
    except Exception as e:
        logger.error(f"Error configurando webhook: {e}")
        return jsonify({'error': str(e)}), 500

# Ruta de salud para Railway
@app.route('/health')
def health_check():
    """Health check para Railway"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# Ruta para favicon
@app.route('/favicon.ico')
def favicon():
    """Servir favicon"""
    from flask import send_from_directory
    import os
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'), 'logo.png', mimetype='image/png')

# Rutas para manejo de archivos médicos
@app.route('/uploads/medical_files/<filename>')
@login_required
def uploaded_file(filename):
    """Servir archivos médicos subidos"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/patient/<patient_id>/exams/upload', methods=['POST'])
@login_required
def upload_exam_file(patient_id):
    """Subir archivo para un examen"""
    try:
        # Verificar que el usuario solo pueda subir sus propios archivos
        if str(session.get('user_id')) != str(patient_id):
            return jsonify({'error': 'No autorizado'}), 403
        
        # Verificar que se envió un archivo
        if 'file' not in request.files:
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
        file = request.files['file']
        exam_id = request.form.get('exam_id')
        
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
        if not exam_id:
            return jsonify({'error': 'ID de examen requerido'}), 400
        
        if file and allowed_file(file.filename):
            # Generar nombre único para el archivo
            filename = generate_unique_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Guardar archivo
            file.save(filepath)
            
            # Actualizar la base de datos con la URL del archivo
            spreadsheet = get_spreadsheet()
            if not spreadsheet:
                # Si no se puede actualizar la BD, eliminar el archivo
                os.remove(filepath)
                return jsonify({'error': 'Error conectando con la base de datos'}), 500
            
            try:
                worksheet = spreadsheet.worksheet('Examenes')
                all_values = worksheet.get_all_values()
                
                # Buscar la fila del examen
                exam_row = None
                if len(all_values) > 1:
                    for i, row in enumerate(all_values[1:], start=2):
                        if len(row) > 1 and str(row[0]) == str(exam_id) and str(row[1]) == str(patient_id):
                            exam_row = i
                            break
                
                if exam_row:
                    # Obtener URLs existentes de archivos
                    current_file_urls = all_values[exam_row - 1][7] if len(all_values[exam_row - 1]) > 7 else ''
                    
                    # Agregar nueva URL a las existentes
                    new_file_url = f"/uploads/medical_files/{filename}"
                    
                    if current_file_urls and current_file_urls.strip():
                        # Si ya hay archivos, agregar el nuevo separado por coma
                        updated_file_urls = f"{current_file_urls},{new_file_url}"
                    else:
                        # Si no hay archivos, usar solo el nuevo
                        updated_file_urls = new_file_url
                    
                    # Actualizar la columna file_url (columna 8, índice H)
                    worksheet.update_cell(exam_row, 8, updated_file_urls)
                    
                    logger.info(f"✅ Archivo agregado al examen {exam_id}: {filename}")
                    logger.info(f"📎 URLs de archivos actualizadas: {updated_file_urls}")
                    
                    return jsonify({
                        'success': True, 
                        'message': 'Archivo subido exitosamente',
                        'file_url': new_file_url,
                        'all_file_urls': updated_file_urls,
                        'filename': filename
                    })
                else:
                    # Si no se encuentra el examen, eliminar el archivo
                    os.remove(filepath)
                    return jsonify({'error': 'Examen no encontrado'}), 404
                    
            except gspread.WorksheetNotFound:
                os.remove(filepath)
                return jsonify({'error': 'Hoja de exámenes no encontrada'}), 404
        else:
            return jsonify({'error': 'Tipo de archivo no permitido. Formatos permitidos: PDF, PNG, JPG, JPEG, GIF, BMP, TIFF, DCM, DICOM, DOC, DOCX, TXT'}), 400
            
    except Exception as e:
        logger.error(f"Error subiendo archivo: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# Manejo de errores
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.route('/api/admin/link-existing-users', methods=['POST'])
@login_required
def link_existing_users():
    """Función de administración para vincular usuarios existentes con sus datos del bot"""
    try:
        # Solo permitir a administradores (por ahora cualquier usuario logueado puede usar esto)
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        users_worksheet = spreadsheet.worksheet('Usuarios')
        all_records = users_worksheet.get_all_records()
        
        results = {
            'users_checked': 0,
            'users_linked': 0,
            'duplicates_found': 0,
            'errors': []
        }
        
        # Buscar usuarios duplicados o sin vincular
        web_users = []  # Usuarios de la plataforma web
        bot_users = []  # Usuarios creados por el bot
        
        for record in all_records:
            user_id = record.get('id') or record.get('user_id', '')
            telegram_id = record.get('telegram_id', '')
            
            if str(user_id).startswith('USR_'):
                # Usuario creado por el bot
                bot_users.append(record)
            else:
                # Usuario de la plataforma web
                web_users.append(record)
            
            results['users_checked'] += 1
        
        # Intentar vincular usuarios basándose en telegram_id
        for bot_user in bot_users:
            bot_telegram_id = bot_user.get('telegram_id', '')
            bot_user_id = bot_user.get('user_id', '')
            
            if bot_telegram_id:
                # Buscar si hay un usuario web que debería estar vinculado a este telegram_id
                matching_web_user = None
                for web_user in web_users:
                    web_telegram_id = web_user.get('telegram_id', '')
                    
                    # Si el usuario web tiene el mismo telegram_id, ya está vinculado
                    if web_telegram_id == bot_telegram_id:
                        matching_web_user = web_user
                        break
                
                # Si encontramos un usuario web con el mismo telegram_id, reportar
                if matching_web_user:
                    results['users_linked'] += 1
                    logger.info(f"✅ Usuario ya vinculado: {matching_web_user.get('nombre')} con telegram_id {bot_telegram_id}")
                else:
                    # Reportar usuario del bot sin vincular
                    results['duplicates_found'] += 1
                    logger.info(f"⚠️ Usuario del bot sin vincular: {bot_user_id} con telegram_id {bot_telegram_id}")
        
        return jsonify({
            'success': True,
            'message': 'Análisis de vinculación completado',
            'results': results,
            'web_users': len(web_users),
            'bot_users': len(bot_users),
            'recommendation': 'Los usuarios pueden vincular sus cuentas manualmente desde la plataforma web'
        })
        
    except Exception as e:
        logger.error(f"Error analizando usuarios: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/user/link-telegram', methods=['POST'])
@login_required
def link_telegram():
    """Vincula la cuenta web del usuario con su cuenta de Telegram"""
    logger.info("🔍 Iniciando link_telegram...")
    try:
        logger.info("📝 Obteniendo datos del request...")
        data = request.get_json()
        logger.info(f"📊 Datos recibidos: {data}")
        
        telegram_id = data.get('telegram_id', '').strip()
        logger.info(f"📱 Telegram ID: {telegram_id}")
        
        if not telegram_id:
            logger.warning("❌ Telegram ID vacío")
            return jsonify({'error': 'ID de Telegram requerido'}), 400
        
        # Obtener el ID del usuario web actual
        user_id = session.get('user_id')
        logger.info(f"👤 User ID de la sesión: {user_id}")
        
        if not user_id:
            logger.warning("❌ Usuario no autenticado")
            return jsonify({'error': 'Usuario no autenticado'}), 401
        
        logger.info("🔗 Conectando con Google Sheets...")
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            logger.error("❌ Error conectando con Google Sheets")
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        logger.info("👤 Obteniendo información del usuario actual...")
        # Verificar que auth_manager esté disponible
        if not auth_manager:
            logger.error("❌ AuthManager no disponible")
            return jsonify({'error': 'Sistema de autenticación no disponible'}), 500
        
        # Obtener información del usuario actual
        try:
            user_info = auth_manager.get_user_by_id(user_id)
            logger.info(f"📝 User info obtenida: {user_info}")
        except Exception as e:
            logger.error(f"❌ Error obteniendo user_info: {e}")
            return jsonify({'error': f'Error obteniendo información del usuario: {str(e)}'}), 500
        
        if not user_info:
            logger.error("❌ Usuario no encontrado en la base de datos")
            return jsonify({'error': 'Información de usuario no encontrada'}), 404
        
        user_name = f"{user_info.get('nombre', '')} {user_info.get('apellido', '')}".strip()
        if not user_name:
            user_name = user_info.get('email', 'Usuario')
        
        logger.info(f"✅ Nombre del usuario: {user_name}")
        
        # Actualizar la hoja de Usuarios para agregar el telegram_id
        try:
            logger.info("📄 Accediendo a la hoja de Usuarios...")
            users_worksheet = spreadsheet.worksheet('Usuarios')
            all_records = users_worksheet.get_all_records()
            logger.info(f"📊 Total de registros de usuarios: {len(all_records)}")
            
            user_row = None
            for i, record in enumerate(all_records, start=2):  # Start from row 2 (after headers)
                record_id = record.get('id') or record.get('user_id', '')
                if str(record_id) == str(user_id):
                    user_row = i
                    logger.info(f"✅ Usuario encontrado en fila: {user_row}")
                    break
            
            if user_row:
                logger.info("🔍 Buscando columna telegram_id...")
                # Buscar la columna telegram_id
                headers = users_worksheet.row_values(1)
                telegram_col = None
                
                if 'telegram_id' in headers:
                    telegram_col = headers.index('telegram_id') + 1
                    logger.info(f"✅ Columna telegram_id encontrada en posición: {telegram_col}")
                else:
                    # Agregar la columna telegram_id si no existe
                    logger.info("➕ Agregando columna telegram_id...")
                    users_worksheet.update_cell(1, len(headers) + 1, 'telegram_id')
                    telegram_col = len(headers) + 1
                    logger.info(f"✅ Columna telegram_id agregada en posición: {telegram_col}")
                
                logger.info(f"💾 Actualizando telegram_id en fila {user_row}, columna {telegram_col}...")
                # Actualizar el telegram_id del usuario
                users_worksheet.update_cell(user_row, telegram_col, telegram_id)
                
                logger.info(f"✅ Usuario {user_id} ({user_name}) vinculado con Telegram ID: {telegram_id}")
                
                # 🚀 ENVIAR MENSAJE DE BIENVENIDA AUTOMÁTICO
                welcome_message = f"""🎉 <b>¡Cuenta Vinculada Exitosamente!</b>

¡Hola <b>{user_name}</b>! 👋

Tu cuenta de MedConnect ha sido vinculada con Telegram correctamente.

✅ <b>Cuenta Web:</b> {user_info.get('email', 'N/A')}
✅ <b>Telegram ID:</b> <code>{telegram_id}</code>

Ahora puedes:
📋 Registrar consultas, medicamentos y exámenes desde Telegram
📊 Ver todo tu historial en la plataforma web
🔄 Los datos se sincronizan automáticamente

<i>¡Gracias por usar MedConnect!</i> 💙"""
                
                logger.info("📨 Enviando mensaje de bienvenida...")
                # Intentar enviar el mensaje
                message_sent = send_telegram_message(telegram_id, welcome_message)
                logger.info(f"📤 Mensaje enviado: {message_sent}")
                
                # Verificar si ya hay datos del bot para este telegram_id
                try:
                    logger.info("🔍 Buscando exámenes del bot...")
                    examenes_worksheet = spreadsheet.worksheet('Examenes')
                    
                    # Leer datos manualmente para evitar error de headers duplicados
                    all_exam_values = examenes_worksheet.get_all_values()
                    examenes_records = []
                    
                    if len(all_exam_values) > 1:
                        headers = all_exam_values[0]
                        for row in all_exam_values[1:]:
                            if len(row) <= len(headers):
                                # Crear diccionario manualmente para evitar conflictos
                                record = {}
                                for i, header in enumerate(headers):
                                    if i < len(row):
                                        record[header] = row[i]
                                examenes_records.append(record)
                    
                    # Buscar exámenes guardados por usuarios del bot con este telegram_id
                    bot_user_ids = []
                    for user_record in all_records:
                        if str(user_record.get('telegram_id', '')) == str(telegram_id):
                            bot_user_id = user_record.get('user_id', '')
                            if str(bot_user_id).startswith('USR_'):
                                bot_user_ids.append(bot_user_id)
                    
                    exams_found = 0
                    for exam_record in examenes_records:
                        if exam_record.get('user_id', '') in bot_user_ids:
                            exams_found += 1
                    
                    logger.info(f"📊 Exámenes encontrados: {exams_found}, Bot users: {len(bot_user_ids)}")
                    
                    return jsonify({
                        'success': True,
                        'message': 'Cuenta de Telegram vinculada exitosamente',
                        'telegram_id': telegram_id,
                        'user_name': user_name,
                        'exams_found': exams_found,
                        'bot_users_found': len(bot_user_ids),
                        'welcome_message_sent': message_sent
                    })
                    
                except gspread.WorksheetNotFound:
                    logger.warning("⚠️ Hoja de Examenes no encontrada")
                    return jsonify({
                        'success': True,
                        'message': 'Cuenta de Telegram vinculada exitosamente',
                        'telegram_id': telegram_id,
                        'user_name': user_name,
                        'exams_found': 0,
                        'bot_users_found': 0,
                        'welcome_message_sent': message_sent
                    })
            else:
                logger.error(f"❌ Usuario {user_id} no encontrado en la hoja de Usuarios")
                return jsonify({'error': 'Usuario no encontrado'}), 404
                
        except Exception as e:
            logger.error(f"❌ Error vinculando Telegram: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"❌ Error en link_telegram: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@app.route('/api/user/telegram-status')
@login_required
def get_telegram_status():
    """Obtiene el estado de vinculación con Telegram del usuario actual"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Usuario no autenticado'}), 401
        
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        users_worksheet = spreadsheet.worksheet('Usuarios')
        all_records = users_worksheet.get_all_records()
        
        telegram_id = None
        for record in all_records:
            if str(record.get('id', '')) == str(user_id):
                telegram_id = record.get('telegram_id', '')
                break
        
        # Convertir telegram_id a string si es necesario
        if telegram_id and not isinstance(telegram_id, str):
            telegram_id = str(telegram_id)
        
        is_linked = bool(telegram_id and telegram_id.strip())
        
        # Si está vinculado, verificar si hay datos del bot
        exams_count = 0
        if is_linked:
            try:
                examenes_worksheet = spreadsheet.worksheet('Examenes')
                
                # Leer datos manualmente para evitar error de headers duplicados
                all_exam_values = examenes_worksheet.get_all_values()
                examenes_records = []
                
                if len(all_exam_values) > 1:
                    headers = all_exam_values[0]
                    for row in all_exam_values[1:]:
                        if len(row) <= len(headers):
                            record = {}
                            for i, header in enumerate(headers):
                                if i < len(row):
                                    record[header] = row[i]
                            examenes_records.append(record)
                
                # Buscar usuarios del bot con este telegram_id
                bot_user_ids = []
                for user_record in all_records:
                    if str(user_record.get('telegram_id', '')) == str(telegram_id):
                        bot_user_id = user_record.get('user_id', '')
                        if bot_user_id.startswith('USR_'):
                            bot_user_ids.append(bot_user_id)
                
                for exam_record in examenes_records:
                    if exam_record.get('user_id', '') in bot_user_ids:
                        exams_count += 1
                        
            except gspread.WorksheetNotFound:
                pass
        
        return jsonify({
            'is_linked': is_linked,
            'telegram_id': telegram_id if is_linked else None,
            'exams_from_bot': exams_count
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estado Telegram: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/patient/<patient_id>/stats')
def get_patient_stats(patient_id):
    """Obtiene las estadísticas del paciente para el dashboard"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        stats = {
            'consultations': 0,
            'medications': 0,
            'exams': 0,
            'health_score': 95  # Valor base, se puede calcular dinámicamente
        }
        
        # Contar consultas
        try:
            consultations_worksheet = spreadsheet.worksheet('Consultas')
            all_values = consultations_worksheet.get_all_values()
            
            if len(all_values) > 1:
                for row in all_values[1:]:
                    if len(row) > 1 and str(row[1]) == str(patient_id):
                        stats['consultations'] += 1
        except gspread.WorksheetNotFound:
            logger.warning("📝 Hoja 'Consultas' no encontrada")
        
        # Contar medicamentos activos
        try:
            medications_worksheet = spreadsheet.worksheet('Medicamentos')
            all_values = medications_worksheet.get_all_values()
            
            if len(all_values) > 1:
                for row in all_values[1:]:
                    if len(row) > 1 and str(row[1]) == str(patient_id):
                        # Solo contar medicamentos activos
                        status = row[8] if len(row) > 8 else 'activo'
                        if status.lower() == 'activo':
                            stats['medications'] += 1
        except gspread.WorksheetNotFound:
            logger.warning("📝 Hoja 'Medicamentos' no encontrada")
        
        # Contar exámenes
        try:
            exams_worksheet = spreadsheet.worksheet('Examenes')
            all_values = exams_worksheet.get_all_values()
            
            if len(all_values) > 1:
                for row in all_values[1:]:
                    if len(row) > 1 and str(row[1]) == str(patient_id):
                        stats['exams'] += 1
        except gspread.WorksheetNotFound:
            logger.warning("📝 Hoja 'Examenes' no encontrada")
        
        # Calcular puntuación de salud básica
        # Fórmula simple: base 85% + bonificaciones
        health_score = 85
        
        # Bonificación por tener consultas recientes
        if stats['consultations'] > 0:
            health_score += min(stats['consultations'] * 2, 10)  # Máximo +10%
        
        # Bonificación por seguir tratamiento
        if stats['medications'] > 0:
            health_score += min(stats['medications'] * 3, 5)  # Máximo +5%
        
        # Asegurar que no exceda 100%
        stats['health_score'] = min(health_score, 100)
        
        logger.info(f"📊 Estadísticas para paciente {patient_id}: {stats}")
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

def convert_date_format(date_str):
    """Convierte fecha de DD/MM/YYYY a YYYY-MM-DD para compatibilidad web"""
    if not date_str or date_str.strip() == '':
        return ''
    
    try:
        # Si ya está en formato YYYY-MM-DD, dejarlo como está
        if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
            return date_str
        
        # Si está en formato DD/MM/YYYY, convertir
        if len(date_str) == 10 and date_str[2] == '/' and date_str[5] == '/':
            day, month, year = date_str.split('/')
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # Si está en formato D/M/YYYY o variaciones, normalizar
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) == 3:
                day, month, year = parts
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # Si no coincide con ningún patrón conocido, devolver como está
        return date_str
        
    except Exception as e:
        logger.warning(f"⚠️ Error convirtiendo fecha '{date_str}': {e}")
        return date_str

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Iniciando MedConnect en puerto {port}")
    logger.info(f"Modo debug: {debug}")
    logger.info(f"Dominio configurado: {app.config['DOMAIN']}")
    
    app.run(host='0.0.0.0', port=port, debug=debug) 