# Guía de Despliegue MedConnect en Railway

Esta guía te ayudará a desplegar MedConnect en Railway con el dominio medconnect.cl.

## Requisitos Previos

1. **Cuenta de Railway**: Crear cuenta en [railway.app](https://railway.app)
2. **Google Sheets**: Hoja de cálculo configurada
3. **Service Account de Google**: Para acceso a Google Sheets API
4. **Bot de Telegram**: Token ya proporcionado
5. **Dominio**: medconnect.cl configurado

## Configuración de Google Sheets

### 1. Crear la Hoja de Cálculo
Crear una nueva hoja de cálculo en Google Sheets con las siguientes pestañas:

- **Pacientes**: Información de usuarios
- **Consultas**: Historial médico
- **Medicamentos**: Medicamentos activos
- **Examenes**: Resultados de exámenes
- **Familiares**: Contactos familiares
- **Interacciones_Bot**: Log del bot de Telegram

### 2. Configurar Service Account
1. Ir a [Google Cloud Console](https://console.cloud.google.com)
2. Crear un nuevo proyecto o seleccionar uno existente
3. Habilitar Google Sheets API y Google Drive API
4. Crear Service Account:
   - Ir a IAM & Admin > Service Accounts
   - Crear nueva cuenta de servicio
   - Descargar el archivo JSON de credenciales
5. Compartir la hoja de cálculo con el email del service account

## Despliegue en Railway

### 1. Conectar Repositorio
```bash
# Clonar el repositorio
git clone [tu-repositorio]
cd medconnect

# Conectar con Railway
railway login
railway init
```

### 2. Configurar Variables de Entorno
En el dashboard de Railway, configurar estas variables:

```env
# Aplicación
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta-muy-segura
DOMAIN=medconnect.cl

# Telegram Bot (ya proporcionado)
TELEGRAM_BOT_TOKEN=7618933472:AAEYCYi9Sso9YVP9aB8dLWvlZ-1hxqgdhck
TELEGRAM_BOT_ID=1071410995

# Google Sheets
GOOGLE_SHEETS_ID=tu-google-sheets-id-aqui
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"..."}

# Email (opcional)
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-password-de-aplicacion
```

### 3. Configurar el Service Account JSON
El contenido completo del archivo JSON del service account debe ir en la variable `GOOGLE_SERVICE_ACCOUNT_JSON`:

```json
{
  "type": "service_account",
  "project_id": "tu-proyecto",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "tu-service-account@tu-proyecto.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

### 4. Desplegar
```bash
# Desplegar a Railway
railway up
```

## Configuración del Dominio

### 1. En Railway
1. Ir a Settings > Domains
2. Agregar custom domain: `medconnect.cl`
3. Configurar subdominios si es necesario

### 2. En tu proveedor de DNS
Configurar los registros DNS:
```
CNAME medconnect.cl -> tu-app.railway.app
CNAME www.medconnect.cl -> tu-app.railway.app
```

## Configuración del Bot de Telegram

### 1. Configurar Webhook
Una vez desplegada la aplicación, configurar el webhook:

```bash
curl -X POST "https://api.telegram.org/bot7618933472:AAEYCYi9Sso9YVP9aB8dLWvlZ-1hxqgdhck/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://medconnect.cl/webhook"}'
```

O visitar: `https://medconnect.cl/setup-webhook`

### 2. Verificar el Bot
1. Buscar `@medconnect_bot` en Telegram
2. Enviar `/start` para probar
3. Verificar que las respuestas se registren en Google Sheets

## Estructura de Carpetas en Producción

```
medconnect/
├── app.py                 # Aplicación principal Flask
├── config.py             # Configuración
├── requirements.txt      # Dependencias Python
├── Procfile             # Comando de inicio para Railway
├── railway.json         # Configuración de Railway
├── templates/           # Templates HTML
│   ├── index.html
│   ├── patient.html
│   └── profile.html
├── static/              # Archivos estáticos
│   ├── css/
│   ├── js/
│   └── images/
└── backend/             # Backend adicional (opcional)
```

## Verificación del Despliegue

### 1. Health Check
Verificar que la aplicación esté funcionando:
```
GET https://medconnect.cl/health
```

### 2. Rutas Principales
- `https://medconnect.cl/` - Landing page
- `https://medconnect.cl/patient` - Dashboard del paciente
- `https://medconnect.cl/profile` - Perfil del usuario
- `https://medconnect.cl/webhook` - Webhook del bot

### 3. Logs
Monitorear los logs en Railway para verificar:
- Conexión exitosa a Google Sheets
- Recepción de webhooks de Telegram
- Errores de la aplicación

## Troubleshooting

### Error de Google Sheets
```
Error inicializando Google Sheets: [Errno -2] Name or service not known
```
**Solución**: Verificar que `GOOGLE_SERVICE_ACCOUNT_JSON` esté correctamente configurado.

### Error de Telegram Webhook
```
Error en webhook: 'message'
```
**Solución**: Verificar que el webhook esté configurado correctamente.

### Error 500 en la aplicación
**Solución**: Revisar los logs de Railway y verificar todas las variables de entorno.

## Comandos Útiles

```bash
# Ver logs en tiempo real
railway logs

# Conectar a la consola
railway shell

# Redeploy
railway up

# Ver variables de entorno
railway variables
```

## Seguridad

1. **Variables de entorno**: Nunca commitear credenciales en el código
2. **HTTPS**: Railway proporciona HTTPS automático
3. **CORS**: Configurado para el dominio medconnect.cl
4. **Webhook**: Solo acepta requests de Telegram

## Mantenimiento

1. **Backups**: Google Sheets actúa como backup automático
2. **Monitoreo**: Usar Railway dashboard para métricas
3. **Updates**: Usar git push para actualizaciones automáticas
4. **Logs**: Revisar logs regularmente para errores

## Soporte

Para problemas técnicos:
1. Revisar logs de Railway
2. Verificar configuración de Google Sheets
3. Probar el bot de Telegram manualmente
4. Verificar conectividad del dominio 