#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para configurar automáticamente Google Sheets para MedConnect
"""

import gspread
from google.oauth2.service_account import Credentials
import json
import sys
from datetime import datetime

# Configuración
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

SERVICE_ACCOUNT_FILE = 'service-account.json'

# Configuración de las hojas
SHEETS_CONFIG = {
    'Pacientes': [
        'id', 'nombre', 'edad', 'telefono', 'email', 
        'fecha_registro', 'plan', 'estado'
    ],
    'Consultas': [
        'id', 'patient_id', 'doctor', 'specialty', 'date', 
        'diagnosis', 'treatment', 'notes', 'status'
    ],
    'Medicamentos': [
        'id', 'patient_id', 'medication', 'dosage', 'frequency',
        'start_date', 'end_date', 'prescribed_by', 'status'
    ],
    'Examenes': [
        'id', 'patient_id', 'exam_type', 'date', 'results',
        'lab', 'doctor', 'file_url', 'status'
    ],
    'Familiares': [
        'id', 'patient_id', 'name', 'relationship', 'phone',
        'email', 'access_level', 'emergency_contact', 'status'
    ],
    'Interacciones_Bot': [
        'id', 'user_id', 'username', 'message', 'response',
        'timestamp', 'action_type', 'status'
    ]
}

def get_google_client():
    """Inicializa el cliente de Google Sheets"""
    try:
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, 
            scopes=SCOPES
        )
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"❌ Error inicializando Google Sheets: {e}")
        return None

def create_medconnect_spreadsheet():
    """Crea una nueva hoja de cálculo para MedConnect"""
    client = get_google_client()
    if not client:
        return None
    
    try:
        # Crear la hoja de cálculo
        spreadsheet = client.create('MedConnect - Base de Datos')
        print(f"✅ Hoja de cálculo creada: {spreadsheet.title}")
        print(f"📋 ID: {spreadsheet.id}")
        print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{spreadsheet.id}")
        
        # Compartir con el service account (ya tiene acceso por defecto)
        # Compartir para que sea editable por el propietario
        try:
            spreadsheet.share('', perm_type='anyone', role='reader')
            print("✅ Hoja compartida como solo lectura para cualquiera con el enlace")
        except:
            print("ℹ️  Permisos de compartir no cambiados (solo el service account tiene acceso)")
        
        return spreadsheet
    except Exception as e:
        print(f"❌ Error creando hoja de cálculo: {e}")
        return None

def setup_worksheets(spreadsheet):
    """Configura todas las hojas de trabajo necesarias"""
    print("\n📊 Configurando hojas de trabajo...")
    
    # Eliminar la hoja por defecto si existe
    try:
        default_sheet = spreadsheet.sheet1
        if default_sheet.title == 'Sheet1' or default_sheet.title == 'Hoja 1':
            spreadsheet.del_worksheet(default_sheet)
            print("🗑️  Hoja por defecto eliminada")
    except:
        pass
    
    # Crear cada hoja con sus columnas
    for sheet_name, columns in SHEETS_CONFIG.items():
        try:
            # Crear la hoja
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=len(columns))
            
            # Agregar encabezados
            worksheet.insert_row(columns, 1)
            
            # Formatear encabezados
            header_range = f"A1:{chr(65 + len(columns) - 1)}1"
            worksheet.format(header_range, {
                "backgroundColor": {"red": 0.36, "green": 0.24, "blue": 0.56},  # Color MedConnect
                "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True},
                "horizontalAlignment": "CENTER"
            })
            
            print(f"✅ Hoja '{sheet_name}' creada con {len(columns)} columnas")
            
        except Exception as e:
            print(f"❌ Error creando hoja '{sheet_name}': {e}")
    
    return True

def add_sample_data(spreadsheet):
    """Agrega datos de ejemplo"""
    print("\n📝 Agregando datos de ejemplo...")
    
    try:
        # Datos de ejemplo para Pacientes
        patients_sheet = spreadsheet.worksheet('Pacientes')
        sample_patients = [
            [1, 'María González', 78, '+56 9 8765 4321', 'maria.gonzalez@email.com', 
             datetime.now().strftime('%Y-%m-%d'), 'Gratuito', 'Activo'],
            [2, 'Carmen Rodríguez', 82, '+56 9 1234 5678', 'carmen.rodriguez@email.com',
             datetime.now().strftime('%Y-%m-%d'), 'Premium', 'Activo']
        ]
        
        for i, patient in enumerate(sample_patients, start=2):
            patients_sheet.insert_row(patient, i)
        
        print("✅ Datos de ejemplo agregados a 'Pacientes'")
        
        # Datos de ejemplo para Consultas
        consultations_sheet = spreadsheet.worksheet('Consultas')
        sample_consultations = [
            [1, 1, 'Dr. Carlos Mendoza', 'Cardiología', '2024-11-15', 
             'Control rutinario', 'Continuar medicación', 'Paciente estable', 'Completada'],
            [2, 1, 'Dra. Ana Rodríguez', 'Traumatología', '2024-11-08',
             'Dolor rodilla', 'Fisioterapia', 'Mejoría progresiva', 'Completada']
        ]
        
        for i, consultation in enumerate(sample_consultations, start=2):
            consultations_sheet.insert_row(consultation, i)
        
        print("✅ Datos de ejemplo agregados a 'Consultas'")
        
        # Datos de ejemplo para Medicamentos
        medications_sheet = spreadsheet.worksheet('Medicamentos')
        sample_medications = [
            [1, 1, 'Losartán 50mg', '50mg', 'Cada 12 horas', '2024-01-01',
             '2024-12-31', 'Dr. Carlos Mendoza', 'Activo'],
            [2, 1, 'Omeprazol 20mg', '20mg', 'En ayunas', '2024-01-01',
             '2024-12-31', 'Dr. Miguel Torres', 'Activo']
        ]
        
        for i, medication in enumerate(sample_medications, start=2):
            medications_sheet.insert_row(medication, i)
        
        print("✅ Datos de ejemplo agregados a 'Medicamentos'")
        
        # Datos de ejemplo para Familiares
        family_sheet = spreadsheet.worksheet('Familiares')
        sample_family = [
            [1, 1, 'Juan González', 'Hijo', '+56 9 8765 4321', 'juan.gonzalez@email.com',
             'Total', True, 'Activo'],
            [2, 1, 'Carmen Pérez', 'Hija', '+56 9 1234 5678', 'carmen.perez@email.com',
             'Familiar', False, 'Activo']
        ]
        
        for i, family in enumerate(sample_family, start=2):
            family_sheet.insert_row(family, i)
        
        print("✅ Datos de ejemplo agregados a 'Familiares'")
        
    except Exception as e:
        print(f"❌ Error agregando datos de ejemplo: {e}")

def test_connection():
    """Prueba la conexión con Google Sheets"""
    print("🔄 Probando conexión con Google Sheets...")
    
    client = get_google_client()
    if not client:
        return False
    
    try:
        # Listar las primeras hojas de cálculo para probar la conexión
        sheets = client.openall()
        print(f"✅ Conexión exitosa. Tienes acceso a {len(sheets)} hojas de cálculo.")
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 MedConnect - Configurador de Google Sheets")
    print("=" * 50)
    
    # Verificar que existe el archivo de credenciales
    try:
        with open(SERVICE_ACCOUNT_FILE, 'r') as f:
            creds_data = json.load(f)
            print(f"✅ Credenciales encontradas para: {creds_data.get('client_email')}")
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo {SERVICE_ACCOUNT_FILE}")
        print("   Por favor, asegúrate de que el archivo esté en el directorio actual.")
        return
    except Exception as e:
        print(f"❌ Error leyendo credenciales: {e}")
        return
    
    # Probar conexión
    if not test_connection():
        return
    
    # Preguntar si crear nueva hoja o usar existente
    print("\n¿Qué deseas hacer?")
    print("1. Crear nueva hoja de cálculo")
    print("2. Usar hoja existente (necesitarás el ID)")
    
    choice = input("\nElige una opción (1 o 2): ").strip()
    
    if choice == '1':
        # Crear nueva hoja
        spreadsheet = create_medconnect_spreadsheet()
        if not spreadsheet:
            return
        
        # Configurar hojas de trabajo
        setup_worksheets(spreadsheet)
        
        # Agregar datos de ejemplo
        add_example = input("\n¿Agregar datos de ejemplo? (s/n): ").strip().lower()
        if add_example in ['s', 'si', 'sí', 'y', 'yes']:
            add_sample_data(spreadsheet)
        
        print(f"\n🎉 ¡Configuración completa!")
        print(f"📋 ID de la hoja: {spreadsheet.id}")
        print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{spreadsheet.id}")
        print(f"\n📝 Para usar en Railway, configura esta variable de entorno:")
        print(f"GOOGLE_SHEETS_ID={spreadsheet.id}")
        
    elif choice == '2':
        # Usar hoja existente
        sheet_id = input("Ingresa el ID de la hoja de cálculo: ").strip()
        
        try:
            client = get_google_client()
            spreadsheet = client.open_by_key(sheet_id)
            print(f"✅ Hoja encontrada: {spreadsheet.title}")
            
            # Configurar hojas de trabajo
            setup_worksheets(spreadsheet)
            
            print(f"\n🎉 ¡Configuración completa!")
            print(f"📋 ID de la hoja: {spreadsheet.id}")
            
        except Exception as e:
            print(f"❌ Error accediendo a la hoja: {e}")
            print("   Verifica que el ID sea correcto y que el service account tenga acceso.")
    
    else:
        print("❌ Opción no válida")

if __name__ == "__main__":
    main() 