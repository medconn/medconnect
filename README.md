<<<<<<< HEAD
# 🏥 MedConnect - Sistema de Gestión Médica Familiar

MedConnect es una plataforma integral que combina una aplicación web con un bot de Telegram para la gestión colaborativa de información médica familiar. Especialmente diseñado para facilitar el cuidado de personas de la tercera edad.

## 🌟 Características Principales

### 🤖 Bot de Telegram Inteligente
- **Gestión familiar completa** con sistema de permisos
- **Notificaciones automáticas** a familiares autorizados
- **Recordatorios de medicamentos** y citas médicas
- **Interfaz con botones** para fácil navegación
- **Subida de archivos médicos** (exámenes, recetas, etc.)

### 🌐 Aplicación Web
- **Dashboard completo** para gestión médica
- **Autenticación segura** de usuarios
- **Interfaz responsive** para móviles y desktop
- **Gestión de perfiles** familiares

### 👨‍👩‍👧‍👦 Sistema Familiar
- **Autorización granular** de familiares (Ver/Editar/Admin)
- **Gestión multi-usuario** fluida
- **Notificaciones en tiempo real**
- **Coordinación entre cuidadores**

### 📊 Base de Datos en Google Sheets
- **Sin costos adicionales** de base de datos
- **Acceso directo** desde Google Sheets
- **Backup automático** en la nube
- **Escalabilidad** según necesidades

## 🚀 Tecnologías Utilizadas

- **Backend**: Python 3.11, Flask
- **Base de Datos**: Google Sheets API
- **Bot**: Telegram Bot API
- **Frontend**: HTML5, CSS3, JavaScript
- **Despliegue**: Railway
- **Autenticación**: Google OAuth2

## 📋 Requisitos Previos

1. **Python 3.11+**
2. **Cuenta de Google** con acceso a Google Sheets API
3. **Bot de Telegram** creado con @BotFather
4. **Cuenta en Railway** para despliegue

## 🛠️ Instalación Local

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/medconnect.git
cd medconnect
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
```bash
cp env.example .env
# Editar .env con tus valores reales
```

### 5. Configurar Google Sheets API

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la API de Google Sheets
4. Crea credenciales de cuenta de servicio
5. Descarga el archivo JSON de credenciales
6. Renómbralo y colócalo en la raíz del proyecto

### 6. Crear Bot de Telegram

1. Habla con [@BotFather](https://t.me/botfather) en Telegram
2. Ejecuta `/newbot` y sigue las instrucciones
3. Guarda el token del bot
4. Configura el token en tu archivo `.env`

### 7. Ejecutar la Aplicación

```bash
# Ejecutar aplicación web
python app.py

# En otra terminal, ejecutar bot
python run_bot.py
```

## 🚀 Despliegue en Railway

### 1. Preparar el Proyecto

```bash
# Asegúrate de que todos los archivos estén actualizados
git add .
git commit -m "Preparar para despliegue en Railway"
git push origin main
```

### 2. Configurar Railway

1. Ve a [Railway.app](https://railway.app)
2. Conecta tu cuenta de GitHub
3. Selecciona "Deploy from GitHub repo"
4. Elige tu repositorio `medconnect`

### 3. Configurar Variables de Entorno en Railway

En el dashboard de Railway, agrega estas variables:

```
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=tu-clave-secreta-super-segura
DOMAIN=tu-dominio-railway.up.railway.app
TELEGRAM_BOT_TOKEN=tu-token-del-bot
GOOGLE_SHEETS_ID=tu-id-de-google-sheets
GOOGLE_CREDENTIALS_FILE=credenciales-codificadas-en-base64
```

### 4. Configurar Credenciales de Google

```bash
# Codificar credenciales en base64
base64 -i tu-archivo-credenciales.json

# Copiar el resultado y pegarlo en GOOGLE_CREDENTIALS_FILE
```

### 5. Configurar Webhook de Telegram

```bash
# Una vez desplegado, configurar webhook
curl -X POST "https://api.telegram.org/bot<TU_TOKEN>/setWebhook?url=https://tu-dominio.railway.app/webhook"
```

## 📖 Guía de Uso

### Para Usuarios (Pacientes)

1. **Registro**: Visita la web y crea tu cuenta
2. **Autorización**: Autoriza familiares desde el bot escribiendo `familiares`
3. **Uso diario**: Interactúa con el bot para registrar información médica

### Para Familiares Autorizados

1. **Autorización**: Pide al usuario principal que te autorice
2. **Gestión**: Usa `🔄 Cambiar Usuario Gestionado` para gestionar familiares
3. **Notificaciones**: Recibirás avisos automáticos de actividad

### Comandos del Bot

- `/mi_info` - Volver a tu información personal
- `/familiares` - Gestión familiar
- `/notificaciones` - Recordatorios y avisos
- `/help` - Ayuda completa

### Palabras Clave

- `familiares` - Menú de gestión familiar
- `documentos` - Ver archivos médicos
- `notificaciones` - Sistema de recordatorios
- `menu` - Menú principal

## 🏗️ Estructura del Proyecto

```
medconnect/
├── app.py                          # Aplicación Flask principal
├── bot.py                          # Bot de Telegram principal
├── run_bot.py                      # Supervisor del bot
├── config.py                       # Configuración del proyecto
├── auth_manager.py                 # Gestión de autenticación
├── requirements.txt                # Dependencias Python
├── Procfile                        # Configuración Railway
├── railway.json                    # Configuración avanzada Railway
├── .gitignore                      # Archivos ignorados por Git
├── env.example                     # Ejemplo de variables de entorno
├── README.md                       # Este archivo
├── backend/
│   ├── api/
│   │   └── flask_api.py           # API REST
│   ├── bot/
│   │   ├── bot_handlers.py        # Manejadores del bot
│   │   └── telegram_bot.py        # Bot alternativo
│   ├── database/
│   │   └── sheets_manager.py      # Gestión Google Sheets
│   └── scripts/
│       └── setup.py               # Scripts de configuración
├── static/
│   ├── css/                       # Estilos CSS
│   ├── js/                        # JavaScript
│   └── images/                    # Imágenes
├── templates/                     # Plantillas HTML
└── docs/                          # Documentación adicional
```

## 🔧 Configuración Avanzada

### Variables de Entorno Completas

```bash
# Flask
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=clave-super-secreta-de-al-menos-32-caracteres

# Dominio
DOMAIN=tu-dominio.com
BASE_URL=https://tu-dominio.com

# Telegram
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_BOT_ID=tu-id-de-telegram
TELEGRAM_WEBHOOK_URL=https://tu-dominio.com/webhook

# Google Sheets
GOOGLE_SHEETS_ID=1ABcdefGHIjklMNOpqrsTUVwxyz-1234567890
GOOGLE_CREDENTIALS_FILE=base64-encoded-credentials

# Logging
LOG_LEVEL=INFO

# Email (opcional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-app-password

# Railway
PORT=5000
RAILWAY_ENVIRONMENT=production
```

## 🛡️ Seguridad

- **Autenticación robusta** con bcrypt
- **Variables de entorno** para datos sensibles
- **Validación de permisos** en cada operación
- **Logs de auditoría** completos
- **HTTPS obligatorio** en producción

## 📊 Monitoreo y Logs

- **Logs estructurados** con timestamps
- **Monitoreo de errores** automático
- **Métricas de uso** del bot
- **Alertas de conectividad**

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Soporte

- **Email**: soporte@medconnect.cl
- **Telegram**: [@medconnect_bot](https://t.me/medconnect_bot)
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/medconnect/issues)

## 🎯 Roadmap

- [ ] App móvil nativa
- [ ] Integración con wearables
- [ ] IA para análisis de síntomas
- [ ] Telemedicina integrada
- [ ] API pública para desarrolladores

---

**Desarrollado con ❤️ para facilitar el cuidado familiar** 
=======
# medconnect
gestión de información de salud de los usuarios
>>>>>>> 5ec6c2179f28499df924b63777794c894f47583d
