"""
API REST de MedConnect
Conecta el frontend React con el backend Python y Google Sheets
"""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import os
from backend.database.sheets_manager import sheets_db
from config import config
import jwt
from functools import wraps

# Configurar Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
CORS(app)

# Configurar logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# === DECORADORES ===

def token_required(f):
    """Decorador para requerir token JWT"""
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token requerido'}), 401
        
        try:
            # Remover 'Bearer ' del token
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
        
        return f(current_user_id, *args, **kwargs)
    return decorator

# === RUTAS DE AUTENTICACIÓN ===

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login de usuario con email/teléfono y código de verificación"""
    try:
        data = request.get_json()
        identifier = data.get('identifier')  # email o teléfono
        
        if not identifier:
            return jsonify({'error': 'Email o teléfono requerido'}), 400
        
        # Buscar usuario por email o teléfono
        # Por simplicidad, buscamos en ambos campos
        # En producción, implementar búsqueda más robusta
        users = sheets_db.get_worksheet('Usuarios').get_all_records()
        user = None
        
        for record in users:
            if (record.get('email') == identifier or 
                record.get('telefono') == identifier):
                user = record
                break
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Generar token JWT
        token = jwt.encode({
            'user_id': user['user_id'],
            'exp': datetime.utcnow() + timedelta(days=30)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'token': token,
            'user': {
                'user_id': user['user_id'],
                'nombre': user['nombre'],
                'email': user['email'],
                'plan': user['plan']
            }
        })
        
    except Exception as e:
        logger.error(f"Error en login: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Registro de nuevo usuario"""
    try:
        data = request.get_json()
        
        required_fields = ['nombre', 'email', 'telefono', 'edad']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} requerido'}), 400
        
        # Verificar si el usuario ya existe
        existing = sheets_db.get_worksheet('Usuarios').get_all_records()
        for record in existing:
            if (record.get('email') == data['email'] or 
                record.get('telefono') == data['telefono']):
                return jsonify({'error': 'Usuario ya existe'}), 409
        
        # Crear usuario
        user_data = {
            'nombre': data['nombre'],
            'apellido': data.get('apellido', ''),
            'email': data['email'],
            'telefono': data['telefono'],
            'edad': data['edad'],
            'direccion': data.get('direccion', ''),
            'rut': data.get('rut', '')
        }
        
        user_id = sheets_db.create_user(user_data)
        
        # Generar token
        token = jwt.encode({
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=30)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'token': token,
            'user_id': user_id,
            'message': 'Usuario registrado exitosamente'
        }), 201
        
    except Exception as e:
        logger.error(f"Error en registro: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# === RUTAS DE USUARIO ===

@app.route('/api/user/profile', methods=['GET'])
@token_required
def get_profile(current_user_id):
    """Obtiene el perfil del usuario"""
    try:
        users = sheets_db.get_worksheet('Usuarios').get_all_records()
        user = None
        
        for record in users:
            if record.get('user_id') == current_user_id:
                user = record
                break
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Obtener estadísticas del usuario
        atenciones = sheets_db.get_user_atenciones(current_user_id)
        medicamentos = sheets_db.get_user_medicamentos_activos(current_user_id)
        familiares = sheets_db.get_familiares_autorizados(current_user_id)
        
        profile = {
            'user_id': user['user_id'],
            'nombre': user['nombre'],
            'apellido': user['apellido'],
            'email': user['email'],
            'telefono': user['telefono'],
            'edad': user['edad'],
            'direccion': user['direccion'],
            'plan': user['plan'],
            'fecha_registro': user['fecha_registro'],
            'estadisticas': {
                'total_atenciones': len(atenciones),
                'medicamentos_activos': len(medicamentos),
                'familiares_autorizados': len(familiares)
            }
        }
        
        return jsonify(profile)
        
    except Exception as e:
        logger.error(f"Error obteniendo perfil: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/user/profile', methods=['PUT'])
@token_required
def update_profile(current_user_id):
    """Actualiza el perfil del usuario"""
    try:
        data = request.get_json()
        
        # Campos actualizables
        updatable_fields = ['nombre', 'apellido', 'email', 'telefono', 'direccion']
        update_data = {}
        
        for field in updatable_fields:
            if field in data:
                update_data[field] = data[field]
        
        if not update_data:
            return jsonify({'error': 'No hay datos para actualizar'}), 400
        
        success = sheets_db.update_user(current_user_id, update_data)
        
        if success:
            return jsonify({'message': 'Perfil actualizado exitosamente'})
        else:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
    except Exception as e:
        logger.error(f"Error actualizando perfil: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# === RUTAS DE ATENCIONES MÉDICAS ===

@app.route('/api/atenciones', methods=['GET'])
@token_required
def get_atenciones(current_user_id):
    """Obtiene las atenciones médicas del usuario"""
    try:
        atenciones = sheets_db.get_user_atenciones(current_user_id)
        
        # Paginar resultados
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        start = (page - 1) * per_page
        end = start + per_page
        
        paginated_atenciones = atenciones[start:end]
        
        return jsonify({
            'atenciones': paginated_atenciones,
            'total': len(atenciones),
            'page': page,
            'per_page': per_page,
            'pages': (len(atenciones) + per_page - 1) // per_page
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo atenciones: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/atenciones', methods=['POST'])
@token_required
def create_atencion(current_user_id):
    """Crea una nueva atención médica"""
    try:
        data = request.get_json()
        
        required_fields = ['fecha', 'hora', 'tipo_atencion', 'especialidad', 
                          'profesional', 'centro_salud', 'diagnostico']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} requerido'}), 400
        
        # Agregar user_id
        data['user_id'] = current_user_id
        
        atencion_id = sheets_db.create_atencion(data)
        
        return jsonify({
            'atencion_id': atencion_id,
            'message': 'Atención registrada exitosamente'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando atención: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# === RUTAS DE MEDICAMENTOS ===

@app.route('/api/medicamentos', methods=['GET'])
@token_required
def get_medicamentos(current_user_id):
    """Obtiene los medicamentos del usuario"""
    try:
        # Obtener parámetro para filtrar activos o todos
        activos_only = request.args.get('activos', 'true').lower() == 'true'
        
        if activos_only:
            medicamentos = sheets_db.get_user_medicamentos_activos(current_user_id)
        else:
            # Obtener todos los medicamentos (implementar método si es necesario)
            medicamentos = sheets_db.get_user_medicamentos_activos(current_user_id)
        
        return jsonify({'medicamentos': medicamentos})
        
    except Exception as e:
        logger.error(f"Error obteniendo medicamentos: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/medicamentos', methods=['POST'])
@token_required
def create_medicamento(current_user_id):
    """Crea un nuevo medicamento"""
    try:
        data = request.get_json()
        
        required_fields = ['nombre_medicamento', 'dosis', 'frecuencia', 
                          'duracion', 'fecha_inicio']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} requerido'}), 400
        
        # Agregar user_id
        data['user_id'] = current_user_id
        
        medicamento_id = sheets_db.create_medicamento(data)
        
        return jsonify({
            'medicamento_id': medicamento_id,
            'message': 'Medicamento registrado exitosamente'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando medicamento: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# === RUTAS DE EXÁMENES ===

@app.route('/api/examenes', methods=['GET'])
@token_required
def get_examenes(current_user_id):
    """Obtiene los exámenes del usuario"""
    try:
        examenes = sheets_db.get_worksheet('Examenes').get_all_records()
        user_examenes = [e for e in examenes if e.get('user_id') == current_user_id]
        
        # Ordenar por fecha más reciente
        user_examenes.sort(
            key=lambda x: datetime.strptime(x.get('fecha_solicitud', '1900-01-01'), '%Y-%m-%d'),
            reverse=True
        )
        
        return jsonify({'examenes': user_examenes})
        
    except Exception as e:
        logger.error(f"Error obteniendo exámenes: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/examenes', methods=['POST'])
@token_required
def create_examen(current_user_id):
    """Crea un nuevo examen"""
    try:
        data = request.get_json()
        
        required_fields = ['tipo_examen', 'nombre_examen', 'fecha_solicitud']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} requerido'}), 400
        
        # Agregar user_id
        data['user_id'] = current_user_id
        
        examen_id = sheets_db.create_examen(data)
        
        return jsonify({
            'examen_id': examen_id,
            'message': 'Examen registrado exitosamente'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando examen: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# === RUTAS DE FAMILIARES ===

@app.route('/api/familiares', methods=['GET'])
@token_required
def get_familiares(current_user_id):
    """Obtiene los familiares autorizados del usuario"""
    try:
        familiares = sheets_db.get_familiares_autorizados(current_user_id)
        return jsonify({'familiares': familiares})
        
    except Exception as e:
        logger.error(f"Error obteniendo familiares: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/familiares', methods=['POST'])
@token_required
def add_familiar(current_user_id):
    """Añade un familiar autorizado"""
    try:
        data = request.get_json()
        
        required_fields = ['nombre_familiar', 'parentesco', 'telefono']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} requerido'}), 400
        
        # Agregar user_id
        data['user_id'] = current_user_id
        
        familiar_id = sheets_db.add_familiar_autorizado(data)
        
        return jsonify({
            'familiar_id': familiar_id,
            'message': 'Familiar autorizado exitosamente'
        }), 201
        
    except Exception as e:
        logger.error(f"Error autorizando familiar: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# === RUTAS DE REPORTES ===

@app.route('/api/reports/summary', methods=['GET'])
@token_required
def get_summary_report(current_user_id):
    """Obtiene un resumen completo del usuario"""
    try:
        summary = sheets_db.get_user_summary(current_user_id)
        return jsonify(summary)
        
    except Exception as e:
        logger.error(f"Error obteniendo resumen: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/reports/export', methods=['GET'])
@token_required
def export_data(current_user_id):
    """Exporta los datos del usuario en formato PDF"""
    try:
        # Implementar generación de PDF con reportlab
        # Por ahora, devolver datos en JSON
        summary = sheets_db.get_user_summary(current_user_id)
        
        # Aquí se implementaría la generación del PDF
        # return send_file(pdf_path, as_attachment=True)
        
        return jsonify({
            'message': 'Función de exportación en desarrollo',
            'data': summary
        })
        
    except Exception as e:
        logger.error(f"Error exportando datos: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# === RUTAS DE SALUD (HEALTH CHECK) ===

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verifica el estado de la API"""
    try:
        # Verificar conexión con Google Sheets
        sheets_db.connect()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'google_sheets': 'connected',
                'api': 'running'
            }
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# === MANEJO DE ERRORES ===

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Método no permitido'}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500

# === INICIO DE LA APLICACIÓN ===

if __name__ == '__main__':
    # Crear directorio de uploads si no existe
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
    
    logger.info("Iniciando MedConnect API...")
    app.run(
        debug=config.FLASK_DEBUG,
        port=config.FLASK_PORT,
        host='0.0.0.0'
    ) 