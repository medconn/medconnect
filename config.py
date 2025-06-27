"""
Configuración general para MedConnect
Manejo de variables de entorno y configuración del sistema
"""
import os
from dotenv import load_dotenv
from datetime import timedelta

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración base para MedConnect"""
    
    # Configuración de la aplicación
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'medconnect-secret-key-2024'
    
    # Configuración del dominio
    DOMAIN = os.environ.get('DOMAIN') or 'medconnect.cl'
    BASE_URL = f"https://{DOMAIN}"
    
    # Configuración de Telegram Bot
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN') or '7618933472:AAEYCYi9Sso9YVP9aB8dLWvlZ-1hxqgdhck'
    TELEGRAM_BOT_ID = os.environ.get('TELEGRAM_BOT_ID') or '1071410995'
    TELEGRAM_WEBHOOK_URL = f"{BASE_URL}/webhook"
    
    # Configuración de Google Sheets
    GOOGLE_SHEETS_ID = os.environ.get('GOOGLE_SHEETS_ID') or '1UvnO2lpZSyv13Hf2eG--kQcTff5BBh7jrZ6taFLJypU'
    GOOGLE_CREDENTIALS_FILE = os.environ.get('GOOGLE_CREDENTIALS_FILE')
    
    # Configuración de la base de datos (Google Sheets como respaldo)
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///medconnect.db'
    
    # Configuración de sesiones
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # Configuración de CORS para el frontend
    CORS_ORIGINS = [
        f"https://{DOMAIN}",
        f"https://www.{DOMAIN}",
        "http://localhost:3000",  # Para desarrollo local
        "http://127.0.0.1:3000"
    ]
    
    # Configuración de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    
    # Configuración de email (para notificaciones)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Configuración de la aplicación
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """Configuración para desarrollo local"""
    DEBUG = True
    BASE_URL = "http://localhost:5000"
    TELEGRAM_WEBHOOK_URL = f"{BASE_URL}/webhook"
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Configuración para producción en Railway"""
    DEBUG = False
    
    # Configuración específica de Railway
    PORT = int(os.environ.get('PORT', 5000))
    
    # Configuración de SSL/TLS
    SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    
    # Configuración de logging para producción
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuración de hojas de Google Sheets
SHEETS_CONFIG = {
    'patients': {
        'name': 'Pacientes',
        'columns': [
            'id', 'nombre', 'edad', 'telefono', 'email', 
            'fecha_registro', 'plan', 'estado'
        ]
    },
    'consultations': {
        'name': 'Consultas',
        'columns': [
            'id', 'patient_id', 'doctor', 'specialty', 'date', 
            'diagnosis', 'treatment', 'notes', 'status'
        ]
    },
    'medications': {
        'name': 'Medicamentos',
        'columns': [
            'id', 'patient_id', 'medication', 'dosage', 'frequency',
            'start_date', 'end_date', 'prescribed_by', 'status'
        ]
    },
    'exams': {
        'name': 'Examenes',
        'columns': [
            'id', 'patient_id', 'exam_type', 'date', 'results',
            'lab', 'doctor', 'file_url', 'status'
        ]
    },
    'family_members': {
        'name': 'Familiares',
        'columns': [
            'id', 'patient_id', 'name', 'relationship', 'phone',
            'email', 'access_level', 'emergency_contact', 'status'
        ]
    },
    'bot_interactions': {
        'name': 'Interacciones_Bot',
        'columns': [
            'id', 'user_id', 'username', 'message', 'response',
            'timestamp', 'action_type', 'status'
        ]
    }
}

# Configuración de Railway
RAILWAY_CONFIG = {
    'build_command': 'pip install -r requirements.txt',
    'start_command': 'python app.py',
    'environment': 'production',
    'auto_deploy': True,
    'domain': 'medconnect.cl'
}

# Configuración según el entorno
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Obtiene la configuración según el entorno"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default']) 