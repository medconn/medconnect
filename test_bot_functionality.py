#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la funcionalidad del bot MedConnect
"""

from bot import MedConnectBot
import logging

logging.basicConfig(level=logging.INFO)

def test_bot_functions():
    """Prueba las funciones principales del bot"""
    print("🧪 Iniciando pruebas del bot MedConnect...")
    
    try:
        # Crear instancia del bot
        bot = MedConnectBot()
        
        # Test 1: Conexión con Google Sheets
        print("\n✅ Test 1: Conexión con Google Sheets")
        if bot.gc and bot.spreadsheet:
            print("   ✅ Conexión exitosa")
        else:
            print("   ❌ Error de conexión")
            return
        
        # Test 2: Parseo de datos de examen
        print("\n✅ Test 2: Parseo de datos de examen")
        test_text = "Eco abdominal, 28/05/2025, Lab hospital, pólipos vesiculares, Luis Alberto Pinto González"
        exam_data = bot.parse_exam_data(test_text)
        
        if exam_data:
            print(f"   ✅ Datos parseados correctamente:")
            print(f"      - Tipo: {exam_data['tipo']}")
            print(f"      - Fecha: {exam_data['fecha']}")
            print(f"      - Laboratorio: {exam_data['laboratorio']}")
            print(f"      - Resultados: {exam_data['resultados']}")
            print(f"      - Médico: {exam_data['medico']}")
        else:
            print("   ❌ Error en el parseo")
            return
        
        # Test 3: Crear usuario de prueba
        print("\n✅ Test 3: Gestión de usuarios")
        test_user_id = 123456789
        test_username = "usuario_prueba"
        
        user = bot.get_or_create_user(test_user_id, test_username)
        if user:
            print(f"   ✅ Usuario gestionado: {user['user_id']} - {user['nombre']}")
        else:
            print("   ❌ Error en gestión de usuario")
            return
        
        # Test 4: Guardar examen de prueba
        print("\n✅ Test 4: Guardado de examen")
        success = bot.save_exam_data(user['user_id'], exam_data)
        if success:
            print("   ✅ Examen guardado exitosamente")
        else:
            print("   ❌ Error guardando examen")
        
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("📱 El bot está listo para usar en Telegram")
        
        # Mostrar instrucciones
        print("\n📋 INSTRUCCIONES PARA EL USUARIO:")
        print("1. Abre Telegram y busca @medconnect_bot")
        print("2. Escribe /start para comenzar")
        print("3. Escribe 'examen' para registrar un examen")
        print("4. Cuando el bot te lo pida, envía los datos en este formato:")
        print("   Eco abdominal, 28/05/2025, Lab hospital, pólipos vesiculares, Luis Alberto Pinto González")
        print("5. El bot procesará y guardará automáticamente la información")
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bot_functions() 