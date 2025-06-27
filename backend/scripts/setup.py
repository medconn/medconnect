#!/usr/bin/env python3
"""
Script de configuración automática para MedConnect
Simplifica la instalación y configuración inicial
"""
import os
import sys
import subprocess
import json
from pathlib import Path

def print_header():
    """Imprime el header de MedConnect"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║                    🏥 MedConnect Setup                       ║
    ║                                                              ║
    ║           Configuración automática del sistema              ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def check_python_version():
    """Verifica la versión de Python"""
    if sys.version_info < (3, 9):
        print("❌ Error: Se requiere Python 3.9 o superior")
        print(f"   Versión actual: {sys.version}")
        sys.exit(1)
    else:
        print(f"✅ Python {sys.version.split()[0]} - OK")

def check_node():
    """Verifica si Node.js está instalado"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js {version} - OK")
            return True
        else:
            print("❌ Node.js no encontrado")
            return False
    except FileNotFoundError:
        print("❌ Node.js no está instalado")
        return False

def create_virtual_environment():
    """Crea el entorno virtual de Python"""
    print("\n📦 Creando entorno virtual...")
    
    if os.path.exists('venv'):
        print("⚠️  El entorno virtual ya existe")
        return True
    
    try:
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("✅ Entorno virtual creado")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error creando entorno virtual")
        return False

def install_python_dependencies():
    """Instala las dependencias de Python"""
    print("\n📥 Instalando dependencias de Python...")
    
    # Determinar el comando pip según el OS
    if os.name == 'nt':  # Windows
        pip_cmd = ['venv\\Scripts\\pip']
    else:  # Linux/Mac
        pip_cmd = ['venv/bin/pip']
    
    try:
        # Actualizar pip
        subprocess.run(pip_cmd + ['install', '--upgrade', 'pip'], check=True)
        
        # Instalar dependencias
        subprocess.run(pip_cmd + ['install', '-r', 'requirements.txt'], check=True)
        
        print("✅ Dependencias de Python instaladas")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

def install_spacy_model():
    """Instala el modelo de spaCy en español"""
    print("\n🔤 Instalando modelo de idioma español...")
    
    if os.name == 'nt':  # Windows
        python_cmd = ['venv\\Scripts\\python']
    else:  # Linux/Mac
        python_cmd = ['venv/bin/python']
    
    try:
        subprocess.run(python_cmd + ['-m', 'spacy', 'download', 'es_core_news_sm'], check=True)
        print("✅ Modelo de español instalado")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  No se pudo instalar el modelo de español (opcional)")
        return True

def install_node_dependencies():
    """Instala las dependencias de Node.js"""
    print("\n📦 Instalando dependencias de Node.js...")
    
    try:
        subprocess.run(['npm', 'install'], check=True)
        print("✅ Dependencias de Node.js instaladas")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error instalando dependencias de Node.js")
        return False

def create_env_file():
    """Crea el archivo .env si no existe"""
    print("\n⚙️  Configurando archivo de entorno...")
    
    if os.path.exists('.env'):
        print("⚠️  El archivo .env ya existe")
        return True
    
    if not os.path.exists('.env.example'):
        print("❌ No se encontró .env.example")
        return False
    
    try:
        # Copiar .env.example a .env
        with open('.env.example', 'r') as src:
            content = src.read()
        
        with open('.env', 'w') as dst:
            dst.write(content)
        
        print("✅ Archivo .env creado")
        print("⚠️  Recuerda configurar las variables en .env")
        return True
    except Exception as e:
        print(f"❌ Error creando .env: {e}")
        return False

def create_directories():
    """Crea los directorios necesarios"""
    print("\n📁 Creando directorios...")
    
    directories = [
        'uploads',
        'logs',
        'backend/database',
        'backend/api',
        'backend/bot',
        'backend/scripts'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Directorios creados")

def create_google_sheets_template():
    """Crea un template para configurar Google Sheets"""
    print("\n📊 Creando template de Google Sheets...")
    
    sheets_config = {
        "instructions": "Configuración de Google Sheets para MedConnect",
        "steps": [
            "1. Ve a https://console.cloud.google.com",
            "2. Crea un nuevo proyecto",
            "3. Habilita Google Sheets API y Google Drive API",
            "4. Crea credenciales de Service Account",
            "5. Descarga el archivo JSON de credenciales",
            "6. Renombra el archivo a 'credentials.json'",
            "7. Crea un nuevo Google Sheets",
            "8. Comparte el sheets con el email del service account",
            "9. Copia el ID del sheets y ponlo en .env"
        ],
        "required_sheets": [
            "Usuarios",
            "Atenciones_Medicas", 
            "Medicamentos",
            "Examenes",
            "Familiares_Autorizados",
            "Logs_Acceso"
        ]
    }
    
    try:
        with open('google_sheets_setup.json', 'w') as f:
            json.dump(sheets_config, f, indent=2)
        
        print("✅ Template de Google Sheets creado: google_sheets_setup.json")
        return True
    except Exception as e:
        print(f"❌ Error creando template: {e}")
        return False

def create_telegram_bot_guide():
    """Crea una guía para configurar el bot de Telegram"""
    guide = """
# 🤖 Configuración del Bot de Telegram

## Pasos para crear el bot:

1. **Abre Telegram** y busca @BotFather
2. **Envía** `/newbot`
3. **Elige un nombre** para tu bot (ej: MedConnect Assistant)
4. **Elige un username** (debe terminar en 'bot', ej: medconnect_assistant_bot)
5. **Copia el token** que te da BotFather
6. **Pega el token** en el archivo .env en la variable TELEGRAM_BOT_TOKEN

## Configurar comandos del bot:

Envía a BotFather:
```
/setcommands
```

Luego copia y pega:
```
start - Iniciar MedConnect
menu - Ir al menú principal  
help - Mostrar ayuda
cancel - Cancelar operación actual
```

## Opcional - Configurar descripción:

```
/setdescription
```

Descripción sugerida:
```
🏥 MedConnect - Tu asistente personal de salud

Registra y gestiona tu información clínica:
• Atenciones médicas
• Medicamentos 
• Exámenes
• Historial familiar

¡Mantén tu salud organizada de forma fácil y segura! 
```

¡Tu bot estará listo para usar!
"""
    
    try:
        with open('telegram_bot_setup.md', 'w') as f:
            f.write(guide)
        
        print("✅ Guía del bot de Telegram creada: telegram_bot_setup.md")
        return True
    except Exception as e:
        print(f"❌ Error creando guía: {e}")
        return False

def create_startup_scripts():
    """Crea scripts para iniciar los servicios"""
    
    # Script para Windows
    windows_script = """@echo off
echo Starting MedConnect...

echo.
echo Starting API...
start "MedConnect API" cmd /k "venv\\Scripts\\activate && python backend/api/flask_api.py"

timeout /t 3

echo.
echo Starting Telegram Bot...
start "MedConnect Bot" cmd /k "venv\\Scripts\\activate && python backend/bot/telegram_bot.py"

timeout /t 3

echo.
echo Starting Frontend...
start "MedConnect Frontend" cmd /k "npm run dev"

echo.
echo MedConnect services are starting...
echo Check the opened windows for status.

pause
"""
    
    # Script para Linux/Mac
    unix_script = """#!/bin/bash
echo "Starting MedConnect..."

echo
echo "Starting API..."
source venv/bin/activate
python backend/api/flask_api.py &
API_PID=$!

sleep 3

echo
echo "Starting Telegram Bot..."
python backend/bot/telegram_bot.py &
BOT_PID=$!

sleep 3

echo
echo "Starting Frontend..."
npm run dev &
FRONTEND_PID=$!

echo
echo "MedConnect services started!"
echo "API PID: $API_PID"
echo "Bot PID: $BOT_PID" 
echo "Frontend PID: $FRONTEND_PID"
echo
echo "To stop all services, run: kill $API_PID $BOT_PID $FRONTEND_PID"
echo
echo "Access the application at: http://localhost:3000"

wait
"""

    try:
        # Crear script de Windows
        with open('start_medconnect.bat', 'w') as f:
            f.write(windows_script)
        
        # Crear script de Unix
        with open('start_medconnect.sh', 'w') as f:
            f.write(unix_script)
        
        # Hacer ejecutable en Unix
        if os.name != 'nt':
            os.chmod('start_medconnect.sh', 0o755)
        
        print("✅ Scripts de inicio creados")
        return True
    except Exception as e:
        print(f"❌ Error creando scripts: {e}")
        return False

def print_next_steps():
    """Imprime los siguientes pasos"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    ✅ INSTALACIÓN COMPLETA                   ║
    ╚══════════════════════════════════════════════════════════════╝
    
    🎉 ¡MedConnect está casi listo!
    
    📋 PRÓXIMOS PASOS:
    
    1. ⚙️  CONFIGURAR VARIABLES DE ENTORNO:
       • Edita el archivo .env
       • Configura TELEGRAM_BOT_TOKEN
       • Configura GOOGLE_SHEETS_ID
       • Coloca credentials.json en el directorio raíz
    
    2. 📊 CONFIGURAR GOOGLE SHEETS:
       • Lee: google_sheets_setup.json
       • Sigue los pasos para crear las APIs
       • Descarga credentials.json
    
    3. 🤖 CONFIGURAR BOT DE TELEGRAM:
       • Lee: telegram_bot_setup.md
       • Crea tu bot con @BotFather
       • Copia el token a .env
    
    4. 🚀 INICIAR MEDCONNECT:
       
       Windows:
       start_medconnect.bat
       
       Linux/Mac:
       ./start_medconnect.sh
    
    5. 🌐 ACCEDER A LA APLICACIÓN:
       • Web: http://localhost:3000
       • Bot: Busca tu bot en Telegram
       • API: http://localhost:5000/api/health
    
    📞 SOPORTE:
    • Lee INSTALL.md para más detalles
    • Revisa los logs en medconnect.log
    • Abre un issue en GitHub si tienes problemas
    
    ¡Gracias por usar MedConnect! 🏥💙
    """)

def main():
    """Función principal del setup"""
    print_header()
    
    print("🔍 Verificando prerrequisitos...")
    check_python_version()
    
    node_available = check_node()
    if not node_available:
        print("\n⚠️  Node.js no está disponible. El frontend no funcionará.")
        response = input("¿Continuar solo con el backend? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print("\n🚀 Iniciando configuración...")
    
    # Configuración de Python
    if not create_virtual_environment():
        sys.exit(1)
    
    if not install_python_dependencies():
        sys.exit(1)
    
    install_spacy_model()  # Opcional
    
    # Configuración de Node.js (si está disponible)
    if node_available:
        if not install_node_dependencies():
            print("⚠️  Error con Node.js, continuando...")
    
    # Configuración general
    create_directories()
    create_env_file()
    create_google_sheets_template()
    create_telegram_bot_guide()
    create_startup_scripts()
    
    print_next_steps()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Configuración cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        sys.exit(1) 