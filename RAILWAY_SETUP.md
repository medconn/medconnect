# 🚂 Guía Completa para Desplegar en Railway

Esta guía te llevará paso a paso para desplegar MedConnect en Railway usando Google Sheets como base de datos.

## 🎯 Prerrequisitos

### ✅ Antes de Comenzar
- [x] Código subido a GitHub
- [x] Cuenta en Railway.app
- [x] Token de Telegram Bot
- [x] Credenciales de Google Sheets
- [x] ID de Google Sheets

## 🔧 Paso 1: Preparar Credenciales

### 1.1 Google Sheets API

1. **Google Cloud Console**: https://console.cloud.google.com/
2. **Crear/Seleccionar Proyecto**
3. **Habilitar APIs**:
   - Google Sheets API
   - Google Drive API
4. **Crear Service Account**:
   - IAM & Admin > Service Accounts
   - Create Service Account
   - Descargar JSON de credenciales
5. **Crear Google Sheets**:
   - Nueva hoja de cálculo
   - Compartir con email del service account (Editor)
   - Copiar ID de la URL

### 1.2 Telegram Bot

1. **BotFather**: https://t.me/botfather
2. **Crear bot**: `/newbot`
3. **Guardar token**: `1234567890:ABCdefGHI...`

### 1.3 Codificar Credenciales

```bash
# En tu computadora local
# Linux/Mac:
base64 -i credenciales.json > credenciales_base64.txt

# Windows:
certutil -encode credenciales.json credenciales_base64.txt

# Copiar TODO el contenido (sin saltos de línea)
```

## 🚂 Paso 2: Configurar Railway

### 2.1 Crear Proyecto

1. **Ir a Railway.app**
2. **Login con GitHub**
3. **New Project**
4. **Deploy from GitHub repo**
5. **Seleccionar `medconnect`**

### 2.2 Configurar Variables de Entorno

En Railway Dashboard > Variables, agregar:

```bash
# Flask Core
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=tu-clave-super-secreta-de-minimo-32-caracteres

# Dominio (Railway lo asigna automáticamente)
DOMAIN=tu-proyecto.up.railway.app
BASE_URL=https://tu-proyecto.up.railway.app

# Telegram
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_BOT_ID=tu-id-de-telegram
TELEGRAM_WEBHOOK_URL=https://tu-proyecto.up.railway.app/webhook

# Google Sheets
GOOGLE_SHEETS_ID=1ABcdefGHIjklMNOpqrsTUVwxyz-1234567890
GOOGLE_CREDENTIALS_FILE=eyJ0eXBlIjoic2VydmljZV9hY2NvdW50IiwicHJvamVjdF9pZCI6InNpbmNlcmUtbWlzc2lvbi00NjM4MDQiLCJwcml2YXRlX2tleV9pZCI6Img5LTk1ZDE2ZWE2MmVmYyIsInByaXZhdGVfa2V5IjoiLS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tXG5NSUlFdlFJQkFEQU5CZ2txaGtpRzl3MEJBUUVGQUFTQ0JLY3dnZ1NqQWdFQUFvSUJBUURGOXM5WEJIWVNcblJnPT1cbi0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS1cbiI...

# Logging
LOG_LEVEL=INFO

# Railway
PORT=5000
RAILWAY_ENVIRONMENT=production
```

### 2.3 Configuración Avanzada

Railway detectará automáticamente:
- `Procfile` para comandos de inicio
- `requirements.txt` para dependencias
- `railway.json` para configuración avanzada

## 🔗 Paso 3: Configurar Webhook

### 3.1 Esperar Despliegue

Railway tardará 2-5 minutos en desplegar. Monitorea en:
- **Deployments** tab
- **Logs** para ver el progreso

### 3.2 Obtener URL de Railway

1. **Ir a Settings > Domains**
2. **Copiar la URL**: `https://tu-proyecto.up.railway.app`

### 3.3 Configurar Webhook de Telegram

```bash
# Reemplazar con tus valores reales
curl -X POST "https://api.telegram.org/bot<TU_TOKEN>/setWebhook?url=https://<TU_DOMINIO>/webhook"

# Ejemplo:
curl -X POST "https://api.telegram.org/bot1234567890:ABCdefGHI/setWebhook?url=https://medconnect-production.up.railway.app/webhook"
```

### 3.4 Verificar Webhook

```bash
curl "https://api.telegram.org/bot<TU_TOKEN>/getWebhookInfo"
```

Respuesta esperada:
```json
{
  "ok": true,
  "result": {
    "url": "https://tu-proyecto.up.railway.app/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

## ✅ Paso 4: Verificar Funcionamiento

### 4.1 Verificar Web App

1. **Abrir**: `https://tu-proyecto.up.railway.app`
2. **Verificar endpoints**:
   - `/` - Página principal ✅
   - `/health` - Estado del servidor ✅
   - `/login` - Página de login ✅

### 4.2 Verificar Bot

1. **Buscar tu bot en Telegram**
2. **Enviar**: `/start`
3. **Probar comandos**:
   - `/help` ✅
   - `menu` ✅
   - `familiares` ✅
   - `/mi_info` ✅

### 4.3 Verificar Google Sheets

1. **Abrir tu Google Sheets**
2. **Usar el bot para registrar información**
3. **Verificar que se guarde en las hojas**

## 📊 Paso 5: Monitoreo

### 5.1 Logs de Railway

```bash
# Ver logs en tiempo real
railway logs --follow

# Ver logs específicos
railway logs --service web
railway logs --service bot
```

### 5.2 Métricas

En Railway Dashboard:
- **CPU Usage**
- **Memory Usage**
- **Network Traffic**
- **Response Times**

### 5.3 Alertas

Configurar en Railway:
- **Deployment failures**
- **High resource usage**
- **Application errors**

## 🐛 Solución de Problemas

### Error: "Application failed to start"

**Posibles causas**:
```bash
# 1. Verificar requirements.txt
railway logs | grep "pip install"

# 2. Verificar variables de entorno
railway variables

# 3. Verificar Procfile
cat Procfile
```

### Error: "Bot not responding"

**Diagnóstico**:
```bash
# 1. Verificar webhook
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"

# 2. Verificar logs del bot
railway logs | grep "bot"

# 3. Verificar variables de Telegram
echo $TELEGRAM_BOT_TOKEN
```

### Error: "Google Sheets access denied"

**Soluciones**:
```bash
# 1. Verificar credenciales base64
echo $GOOGLE_CREDENTIALS_FILE | base64 -d

# 2. Verificar permisos en Google Sheets
# - Compartir hoja con service account email
# - Rol: Editor

# 3. Verificar GOOGLE_SHEETS_ID
echo $GOOGLE_SHEETS_ID
```

### Error: "Import errors"

```bash
# Verificar estructura de archivos
railway run ls -la
railway run ls -la backend/
railway run ls -la backend/database/

# Verificar imports
railway run python -c "from backend.database.sheets_manager import SheetsManager"
```

## 🔄 Actualizaciones

### Proceso de Actualización

```bash
# 1. Local: hacer cambios
git add .
git commit -m "Descripción del cambio"
git push origin main

# 2. Railway redesplegará automáticamente
# 3. Monitorear logs durante el despliegue
railway logs --follow
```

### Rollback en caso de errores

```bash
# En Railway Dashboard:
# Deployments > Seleccionar versión anterior > Redeploy
```

## 🎯 Configuración Opcional

### Dominio Personalizado

1. **Railway Dashboard > Settings > Domains**
2. **Add Custom Domain**
3. **Configurar DNS**:
   ```
   CNAME: tu-dominio.com -> tu-proyecto.up.railway.app
   ```

### Variables de Entorno Adicionales

```bash
# Email (opcional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-app-password

# CORS (si necesario)
CORS_ORIGINS=https://tu-dominio.com,https://otro-dominio.com
```

## 📋 Checklist Final

### ✅ Verificación Completa

- [ ] ✅ Railway proyecto creado
- [ ] ✅ Código desplegado desde GitHub
- [ ] ✅ Variables de entorno configuradas
- [ ] ✅ Webhook de Telegram funcionando
- [ ] ✅ Google Sheets conectado y escribiendo
- [ ] ✅ Bot respondiendo a comandos
- [ ] ✅ Web app cargando correctamente
- [ ] ✅ Sistema familiar operativo
- [ ] ✅ Notificaciones funcionando
- [ ] ✅ Logs sin errores críticos
- [ ] ✅ Monitoreo configurado

## 🎉 ¡Éxito!

Tu sistema MedConnect está ahora **desplegado y funcionando** en Railway. 

### 🌟 Funcionalidades Activas

- **🌐 Web App**: Accesible desde cualquier navegador
- **🤖 Bot Telegram**: Disponible 24/7 para usuarios
- **👨‍👩‍👧‍👦 Gestión Familiar**: Sistema completo de permisos
- **📊 Google Sheets**: Base de datos funcionando
- **🔔 Notificaciones**: Alertas automáticas a familiares
- **📱 Recordatorios**: Sistema de medicamentos y citas

### 📞 URLs Importantes

- **Web App**: `https://tu-proyecto.up.railway.app`
- **Bot Telegram**: `@tu_bot_username`
- **Railway Dashboard**: `https://railway.app/project/tu-proyecto`
- **Google Sheets**: `https://docs.google.com/spreadsheets/d/tu-sheets-id`

**¡El sistema está listo para ayudar a familias a cuidar mejor de sus seres queridos!** 🏥💙 