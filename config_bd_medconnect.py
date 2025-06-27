#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para configurar específicamente la hoja bd_medconnect
"""

import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime

# Configuración
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

SERVICE_ACCOUNT_FILE = 'service-account.json'
SHEET_ID = '1UvnO2lpZSyv13Hf2eG--kQcTff5BBh7jrZ6taFLJypU'

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

def setup_bd_medconnect():
    """Configura la hoja bd_medconnect"""
    print("🚀 Configurando bd_medconnect para MedConnect")
    print("=" * 50)
    
    client = get_google_client()
    if not client:
        return False
    
    try:
        # Abrir la hoja existente
        spreadsheet = client.open_by_key(SHEET_ID)
        print(f"✅ Hoja encontrada: {spreadsheet.title}")
        print(f"📋 ID: {spreadsheet.id}")
        
        # Verificar hojas existentes
        existing_worksheets = [ws.title for ws in spreadsheet.worksheets()]
        print(f"📊 Hojas existentes: {', '.join(existing_worksheets)}")
        
        # Configurar cada hoja necesaria
        for sheet_name, columns in SHEETS_CONFIG.items():
            print(f"\n🔄 Configurando hoja '{sheet_name}'...")
            
            try:
                # Verificar si la hoja ya existe
                if sheet_name in existing_worksheets:
                    worksheet = spreadsheet.worksheet(sheet_name)
                    print(f"   ℹ️  Hoja '{sheet_name}' ya existe, actualizando encabezados...")
                else:
                    # Crear nueva hoja
                    worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=len(columns))
                    print(f"   ✅ Hoja '{sheet_name}' creada")
                
                # Configurar encabezados
                worksheet.clear()  # Limpiar contenido existente
                worksheet.insert_row(columns, 1)
                
                # Formatear encabezados
                header_range = f"A1:{chr(65 + len(columns) - 1)}1"
                worksheet.format(header_range, {
                    "backgroundColor": {"red": 0.36, "green": 0.24, "blue": 0.56},  # Color MedConnect
                    "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True},
                    "horizontalAlignment": "CENTER"
                })
                
                print(f"   ✅ Encabezados configurados ({len(columns)} columnas)")
                
            except Exception as e:
                print(f"   ❌ Error configurando '{sheet_name}': {e}")
        
        # Eliminar hoja por defecto si existe y no es necesaria
        try:
            default_sheets = ['Hoja 1', 'Sheet1', 'Hoja1']
            for default_name in default_sheets:
                if default_name in existing_worksheets and default_name not in SHEETS_CONFIG:
                    default_sheet = spreadsheet.worksheet(default_name)
                    spreadsheet.del_worksheet(default_sheet)
                    print(f"🗑️  Hoja por defecto '{default_name}' eliminada")
        except Exception as e:
            print(f"ℹ️  No se pudo eliminar hoja por defecto: {e}")
        
        # Agregar datos de ejemplo
        add_sample_data(spreadsheet)
        
        print(f"\n🎉 ¡Configuración completa!")
        print(f"📋 ID para Railway: {SHEET_ID}")
        print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{SHEET_ID}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error configurando hoja: {e}")
        return False

def add_sample_data(spreadsheet):
    """Agrega datos de ejemplo"""
    print(f"\n📝 Agregando datos de ejemplo...")
    
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
        
        print("   ✅ Datos agregados a 'Pacientes'")
        
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
        
        print("   ✅ Datos agregados a 'Consultas'")
        
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
        
        print("   ✅ Datos agregados a 'Medicamentos'")
        
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
        
        print("   ✅ Datos agregados a 'Familiares'")
        
    except Exception as e:
        print(f"   ⚠️  Algunos datos de ejemplo no se pudieron agregar: {e}")

def main():
    """Función principal"""
    print("🔧 MedConnect - Configurador Automático bd_medconnect")
    print("=" * 60)
    
    # Verificar credenciales
    try:
        with open(SERVICE_ACCOUNT_FILE, 'r') as f:
            creds_data = json.load(f)
            print(f"✅ Credenciales: {creds_data.get('client_email')}")
    except Exception as e:
        print(f"❌ Error con credenciales: {e}")
        return
    
    print(f"🎯 Configurando hoja ID: {SHEET_ID}")
    
    # Configurar la hoja
    if setup_bd_medconnect():
        print(f"\n🚀 ¡Listo para Railway!")
        print(f"📝 Variable de entorno necesaria:")
        print(f"GOOGLE_SHEETS_ID={SHEET_ID}")
    else:
        print(f"\n❌ Error en la configuración")

if __name__ == "__main__":
    main() 