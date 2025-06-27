# MedConnect - Configuración Completa

## Resumen del Proyecto

**MedConnect** es una plataforma digital especializada en gestión de información clínica y acompañamiento familiar para adultos mayores, con las siguientes características:

### Tecnologías Implementadas
- **Backend**: Flask (Python)
- **Base de datos**: Google Sheets
- **Bot**: Telegram (@medconnect_bot)
- **Frontend**: HTML5, CSS3, JavaScript
- **Despliegue**: Railway
- **Dominio**: medconnect.cl

## Configuración del Bot de Telegram

### Credenciales Proporcionadas
```
Token: 7618933472:AAEYCYi9Sso9YVP9aB8dLWvlZ-1hxqgdhck
Bot ID: 1071410995
Username: @medconnect_bot
```

### Funcionalidades del Bot
- Registro de consultas médicas
- Gestión de medicamentos
- Registro de exámenes
- Consulta de historial
- Notificaciones familiares
- Respuestas automáticas inteligentes

## Estructura de Google Sheets

### Hojas Requeridas:
1. **Pacientes** - Información de usuarios
2. **Consultas** - Historial médico
3. **Medicamentos** - Medicamentos activos
4. **Examenes** - Resultados de exámenes
5. **Familiares** - Contactos familiares
6. **Interacciones_Bot** - Log del bot

### Columnas por Hoja:

#### Pacientes
- id, nombre, edad, telefono, email, fecha_registro, plan, estado

#### Consultas
- id, patient_id, doctor, specialty, date, diagnosis, treatment, notes, status

#### Medicamentos
- id, patient_id, medication, dosage, frequency, start_date, end_date, prescribed_by, status

#### Examenes
- id, patient_id, exam_type, date, results, lab, doctor, file_url, status

#### Familiares
- id, patient_id, name, relationship, phone, email, access_level, emergency_contact, status

#### Interacciones_Bot
- id, user_id, username, message, response, timestamp, action_type, status

## Archivos de Configuración

### 1. app.py - Aplicación Principal
- Servidor Flask configurado para Railway
- Integración completa con Google Sheets
- Webhook de Telegram configurado
- API endpoints para el frontend
- Manejo de errores y logging

### 2. config.py - Configuración
- Variables de entorno para desarrollo y producción
- Configuración de Google Sheets
- Settings de Telegram Bot
- Configuración de Railway y dominio

### 3. requirements.txt - Dependencias
- Flask y extensiones
- Google Sheets API
- Requests para Telegram
- Gunicorn para producción

### 4. Procfile - Railway
```
web: gunicorn --bind 0.0.0.0:$PORT app:app --workers 4 --timeout 120
```

### 5. railway.json - Configuración Railway
- Build y deploy commands
- Variables de entorno
- Health check configurado

## Estructura de Carpetas

```
medconnect/
├── app.py                    # Aplicación Flask principal
├── config.py                # Configuración
├── requirements.txt         # Dependencias Python
├── Procfile                 # Comando Railway
├── railway.json            # Config Railway
├── .gitignore              # Archivos a ignorar
├── DEPLOY.md               # Guía de despliegue
├── templates/              # Templates HTML
│   ├── index.html         # Landing page
│   ├── patient.html       # Dashboard paciente
│   ├── profile.html       # Perfil usuario
│   ├── professional.html  # Dashboard profesional
│   └── otros...
├── static/                 # Archivos estáticos
│   ├── css/
│   │   ├── patient-styles.css
│   │   ├── professional-styles.css
│   │   └── styles.css
│   ├── js/
│   │   ├── patient.js
│   │   ├── professional.js
│   │   └── app.js
│   └── images/
│       ├── logo.png
│       └── Imagen2.png
└── backend/               # Backend adicional
    ├── api/
    ├── bot/
    └── database/
```

## Variables de Entorno para Railway

```env
# Aplicación
FLASK_ENV=production
SECRET_KEY=medconnect-secret-key-2024
DOMAIN=medconnect.cl

# Telegram Bot
TELEGRAM_BOT_TOKEN=7618933472:AAEYCYi9Sso9YVP9aB8dLWvlZ-1hxqgdhck
TELEGRAM_BOT_ID=1071410995

# Google Sheets
GOOGLE_SHEETS_ID=[ID de tu hoja de Google Sheets]
GOOGLE_SERVICE_ACCOUNT_JSON=[JSON completo del service account]

# Email (opcional)
MAIL_USERNAME=[tu-email@gmail.com]
MAIL_PASSWORD=[password-de-aplicacion]

# Logging
LOG_LEVEL=INFO
```

## Rutas de la Aplicación

### Frontend
- `/` - Landing page
- `/patient` - Dashboard del paciente
- `/professional` - Dashboard del profesional
- `/profile` - Perfil del usuario

### API
- `/api/patient/<id>/consultations` - Consultas del paciente
- `/api/patient/<id>/medications` - Medicamentos del paciente
- `/api/patient/<id>/exams` - Exámenes del paciente

### Telegram
- `/webhook` - Webhook del bot
- `/setup-webhook` - Configurar webhook

### Utilidades
- `/health` - Health check para Railway

## Funcionalidades Implementadas

### Dashboard del Paciente
- ✅ Header con información del usuario
- ✅ Acciones rápidas (ChatBot, Agendar, Reportes, Emergencia)
- ✅ Tabs de navegación (Historial, Medicamentos, Exámenes, Familia)
- ✅ Diseño responsive y accesible
- ✅ Colores oficiales de MedConnect
- ✅ Funcionalidad de logout

### Bot de Telegram
- ✅ Comando /start con bienvenida
- ✅ Registro de consultas médicas
- ✅ Gestión de medicamentos
- ✅ Registro de exámenes
- ✅ Consulta de historial
- ✅ Logging en Google Sheets

### Interfaz
- ✅ Diseño moderno estilo Google Drive
- ✅ Paleta de colores oficial MedConnect
- ✅ Logo oficial integrado
- ✅ Responsive design
- ✅ Accesibilidad para adultos mayores

## Próximos Pasos para Despliegue

### 1. Configurar Google Sheets
1. Crear nueva hoja de cálculo
2. Crear las 6 pestañas con columnas especificadas
3. Configurar Service Account en Google Cloud
4. Compartir hoja con service account

### 2. Desplegar en Railway
1. Conectar repositorio a Railway
2. Configurar variables de entorno
3. Configurar dominio medconnect.cl
4. Hacer deploy

### 3. Configurar Telegram Bot
1. Configurar webhook: `https://medconnect.cl/webhook`
2. Probar bot con comando /start
3. Verificar logging en Google Sheets

### 4. Verificación Final
- [ ] Aplicación accesible en medconnect.cl
- [ ] Bot respondiendo correctamente
- [ ] Google Sheets recibiendo datos
- [ ] Dashboard funcionando
- [ ] Health check respondiendo

## Comandos de Despliegue

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login y conectar proyecto
railway login
railway init

# Configurar variables de entorno
railway variables set FLASK_ENV=production
railway variables set DOMAIN=medconnect.cl
# ... (todas las variables)

# Desplegar
railway up

# Ver logs
railway logs

# Configurar webhook del bot
curl -X POST "https://api.telegram.org/bot7618933472:AAEYCYi9Sso9YVP9aB8dLWvlZ-1hxqgdhck/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://medconnect.cl/webhook"}'
```

## Soporte y Mantenimiento

### Monitoreo
- Railway dashboard para métricas
- Google Sheets para datos
- Telegram bot para interacciones

### Logs
- Railway logs para errores de aplicación
- Google Sheets para interacciones del bot
- Health check para disponibilidad

### Backups
- Google Sheets actúa como backup automático
- Railway mantiene historial de deployments
- Git para control de versiones del código

---

**Estado**: ✅ Configuración completa lista para despliegue
**Próximo paso**: Configurar Google Sheets y desplegar en Railway 