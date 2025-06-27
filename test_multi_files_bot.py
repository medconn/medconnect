#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script de prueba para funcionalidad de múltiples archivos del bot"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot import MedConnectBot
import tempfile
import uuid

def test_multiple_files():
    """Prueba la funcionalidad de múltiples archivos"""
    
    print("🧪 === PRUEBA DE MÚLTIPLES ARCHIVOS ===")
    
    # Inicializar bot
    bot = MedConnectBot()
    
    # Simular usuario de prueba
    test_user_id = 999999999
    test_username = "test_user"
    
    print(f"👤 Usuario de prueba: {test_user_id}")
    
    # Crear archivos de prueba temporales
    test_files = []
    
    # Crear archivo PDF de prueba
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n202\n%%EOF"
    
    # Crear archivo de imagen de prueba (PNG mínimo)
    png_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x12IDATx\x9cc\xf8\x0f\x00\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00IEND\xaeB`\x82'
    
    # Simular archivos recibidos
    files_data = [
        {
            'file_id': f'test_pdf_{uuid.uuid4().hex}',
            'file_name': 'informe_medico.pdf',
            'file_size': len(pdf_content),
            'content': pdf_content
        },
        {
            'file_id': f'test_png_{uuid.uuid4().hex}',
            'file_name': 'radiografia.png', 
            'file_size': len(png_content),
            'content': png_content
        }
    ]
    
    print(f"📎 Simulando {len(files_data)} archivos:")
    for i, file_data in enumerate(files_data, 1):
        print(f"   {i}. {file_data['file_name']} ({file_data['file_size']} bytes)")
    
    # Simular procesamiento de archivos
    success_count = 0
    
    for file_data in files_data:
        # Simular descarga exitosa (en lugar de descargar de Telegram)
        print(f"📥 Procesando archivo: {file_data['file_name']}")
        
        # Simular guardado de archivo
        if bot.allowed_file(file_data['file_name']):
            unique_filename = bot.generate_unique_filename(file_data['file_name'])
            filepath = os.path.join(bot.upload_folder, unique_filename)
            
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Guardar archivo
            with open(filepath, 'wb') as f:
                f.write(file_data['content'])
            
            # Agregar a estado del usuario
            if test_user_id not in bot.user_files:
                bot.user_files[test_user_id] = []
                
            file_url = f"/uploads/medical_files/{unique_filename}"
            bot.user_files[test_user_id].append({
                'filename': unique_filename,
                'original_name': file_data['file_name'],
                'file_url': file_url,
                'file_type': 'document' if file_data['file_name'].endswith('.pdf') else 'photo'
            })
            
            success_count += 1
            print(f"   ✅ Guardado como: {unique_filename}")
            test_files.append(filepath)
        else:
            print(f"   ❌ Tipo de archivo no permitido")
    
    print(f"\n📊 Archivos procesados exitosamente: {success_count}/{len(files_data)}")
    print(f"📁 Archivos en estado del usuario: {len(bot.user_files.get(test_user_id, []))}")
    
    # Mostrar archivos almacenados
    if test_user_id in bot.user_files:
        print("\n📋 Archivos almacenados:")
        for i, file_info in enumerate(bot.user_files[test_user_id], 1):
            print(f"   {i}. {file_info['original_name']} -> {file_info['file_url']}")
    
    # Simular guardado de examen con archivos
    print("\n🩺 Simulando guardado de examen con archivos...")
    
    exam_data = {
        'tipo': 'Eco abdominal',
        'fecha': '28/12/2024',
        'laboratorio': 'Lab Test Hospital',
        'resultados': 'Examen normal, sin alteraciones',
        'medico': 'Dr. Test González'
    }
    
    # Crear usuario de prueba si no existe
    user = bot.get_or_create_user(test_user_id, test_username)
    if user:
        print(f"👤 Usuario encontrado/creado: {user.get('user_id', 'N/A')}")
        
        # Los archivos están almacenados con test_user_id, pero save_exam_data usa user['user_id']
        # Copiar archivos al user_id correcto
        if test_user_id in bot.user_files and user['user_id'] != test_user_id:
            bot.user_files[user['user_id']] = bot.user_files[test_user_id]
            del bot.user_files[test_user_id]
            print(f"📁 Archivos movidos de {test_user_id} a {user['user_id']}")
        
        # Intentar guardar examen
        if bot.save_exam_data(user['user_id'], exam_data):
            print("✅ Examen guardado exitosamente con archivos adjuntos")
        else:
            print("❌ Error guardando examen")
    else:
        print("❌ Error creando/obteniendo usuario")
    
    # Limpiar archivos de prueba
    print("\n🧹 Limpiando archivos de prueba...")
    for filepath in test_files:
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"   🗑️ Eliminado: {filepath}")
        except Exception as e:
            print(f"   ⚠️ Error eliminando {filepath}: {e}")
    
    print("\n✅ Prueba completada")

def test_file_validation():
    """Prueba la validación de archivos"""
    print("\n🧪 === PRUEBA DE VALIDACIÓN DE ARCHIVOS ===")
    
    bot = MedConnectBot()
    
    test_cases = [
        ('documento.pdf', True),
        ('imagen.jpg', True),
        ('foto.png', True),
        ('informe.doc', True),
        ('resultado.docx', True),
        ('notas.txt', True),
        ('virus.exe', False),
        ('script.js', False),
        ('archivo.xyz', False),
        ('', False),
        ('archivo_sin_extension', False)
    ]
    
    print("📝 Probando validación de extensiones:")
    for filename, expected in test_cases:
        result = bot.allowed_file(filename) if filename else False
        status = "✅" if result == expected else "❌"
        print(f"   {status} {filename or '(vacío)'}: {result} (esperado: {expected})")

def test_unique_filename():
    """Prueba la generación de nombres únicos"""
    print("\n🧪 === PRUEBA DE NOMBRES ÚNICOS ===")
    
    bot = MedConnectBot()
    
    original_files = [
        'informe.pdf',
        'radiografia.jpg',
        'resultado.docx'
    ]
    
    print("🔤 Generando nombres únicos:")
    for original in original_files:
        unique = bot.generate_unique_filename(original)
        print(f"   {original} -> {unique}")

if __name__ == "__main__":
    try:
        test_file_validation()
        test_unique_filename()
        test_multiple_files()
        print("\n🎉 Todas las pruebas completadas exitosamente")
    except Exception as e:
        print(f"\n💥 Error en las pruebas: {e}")
        import traceback
        traceback.print_exc() 