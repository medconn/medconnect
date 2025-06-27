#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para la integración completa entre bot y plataforma web
"""

import requests
import json
from bot import MedConnectBot
import logging

logging.basicConfig(level=logging.INFO)

def test_complete_integration():
    """Prueba la integración completa del sistema"""
    print("🧪 Iniciando prueba de integración completa...")
    
    try:
        # 1. Probar bot de Telegram
        print("\n🤖 Test 1: Funcionalidad del bot")
        bot = MedConnectBot()
        
        if not bot.gc or not bot.spreadsheet:
            print("❌ Error: Bot no conectado con Google Sheets")
            return
        
        print("✅ Bot conectado correctamente")
        
        # 2. Simular registro de examen por bot
        print("\n📝 Test 2: Simulando registro de examen por bot")
        test_user_id = 1071410995  # ID de Telegram de prueba
        test_username = "test_user"
        
        # Crear usuario
        user = bot.get_or_create_user(test_user_id, test_username)
        if not user:
            print("❌ Error creando usuario")
            return
        
        print(f"✅ Usuario creado/encontrado: {user['user_id']}")
        
        # Simular datos de examen
        exam_text = "Hemograma completo, 24/06/2025, Lab Central, valores normales, Dr. García"
        exam_data = bot.parse_exam_data(exam_text)
        
        if not exam_data:
            print("❌ Error parseando datos de examen")
            return
        
        print(f"✅ Datos parseados: {exam_data}")
        
        # Guardar examen
        success = bot.save_exam_data(user['user_id'], exam_data)
        if not success:
            print("❌ Error guardando examen")
            return
        
        print("✅ Examen guardado exitosamente")
        
        # 3. Verificar que los datos están en Google Sheets
        print("\n📊 Test 3: Verificando datos en Google Sheets")
        try:
            examenes_worksheet = bot.spreadsheet.worksheet('Examenes')
            records = examenes_worksheet.get_all_records()
            
            user_exams = [r for r in records if r.get('user_id') == user['user_id']]
            print(f"✅ Exámenes encontrados en Sheets: {len(user_exams)}")
            
            if user_exams:
                latest_exam = user_exams[-1]
                print(f"   📋 Último examen: {latest_exam.get('tipo_examen')} - {latest_exam.get('resultado')}")
            
        except Exception as e:
            print(f"❌ Error verificando Sheets: {e}")
            return
        
        # 4. Información para el usuario
        print("\n🎯 Test 4: Información para vincular cuentas")
        print(f"   📱 ID de Telegram: {test_user_id}")
        print(f"   🆔 User ID del bot: {user['user_id']}")
        print(f"   📊 Exámenes registrados: {len(user_exams)}")
        
        print("\n✅ ¡Integración funcionando correctamente!")
        
        # Instrucciones para el usuario
        print("\n📋 INSTRUCCIONES PARA EL USUARIO:")
        print("1. 🔗 Abrir la plataforma web y ir a tu dashboard")
        print("2. 📱 Hacer clic en la pestaña 'Integración con Telegram'")
        print(f"3. 📝 Ingresar tu ID de Telegram: {test_user_id}")
        print("4. 🔄 Hacer clic en 'Vincular'")
        print("5. 📊 Ir a la pestaña 'Exámenes' para ver los datos")
        print("\n🚀 Una vez vinculado, todos los datos del bot aparecerán en la web!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_user_instructions():
    """Muestra instrucciones detalladas para el usuario"""
    print("\n" + "="*60)
    print("📱 GUÍA COMPLETA DE USO - MEDCONNECT")
    print("="*60)
    
    print("\n🤖 USAR EL BOT DE TELEGRAM:")
    print("1. Abre Telegram")
    print("2. Busca: @medconnect_bot")
    print("3. Envía: /start")
    print("4. Copia tu ID de Telegram (aparece en la respuesta)")
    print("5. Para registrar examen, envía: examen")
    print("6. Proporciona datos así: Eco abdominal, 28/05/2025, Lab hospital, pólipos vesiculares, Dr. Pinto")
    
    print("\n🌐 VINCULAR CON LA PLATAFORMA WEB:")
    print("1. Abre: https://medconnect.cl/login")
    print("2. Inicia sesión con tu cuenta")
    print("3. Ve a tu dashboard")
    print("4. Clic en pestaña: 'Integración con Telegram'")
    print("5. Pega tu ID de Telegram")
    print("6. Clic en 'Vincular'")
    
    print("\n✨ BENEFICIOS DE LA INTEGRACIÓN:")
    print("• 📊 Todos los datos del bot aparecen en la web")
    print("• 🔄 Sincronización automática")
    print("• 📱 Registra desde Telegram, ve en la web")
    print("• 🏥 Historial médico unificado")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    success = test_complete_integration()
    
    if success:
        show_user_instructions()
    else:
        print("\n❌ Algunas pruebas fallaron. Revisa los errores arriba.") 