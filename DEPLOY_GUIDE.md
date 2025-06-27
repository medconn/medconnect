# 🚀 Guía Completa de Despliegue - MedConnect

Esta guía te llevará paso a paso para subir MedConnect a GitHub y desplegarlo en Railway.

## 📋 Checklist Pre-Despliegue

### ✅ Archivos de Configuración
- [x] `.gitignore` - Excluye archivos sensibles
- [x] `requirements.txt` - Dependencias actualizadas
- [x] `Procfile` - Comandos de Railway
- [x] `railway.json` - Configuración avanzada
- [x] `env.example` - Ejemplo de variables de entorno
- [x] `README.md` - Documentación completa

### ✅ Credenciales y Configuración
- [ ] Token de Telegram Bot
- [ ] Credenciales de Google Sheets
- [ ] ID de Google Sheets
- [ ] Variables de entorno configuradas

## 🔧 Paso 1: Preparar Credenciales

### 1.1 Configurar Google Sheets API

1. **Crear proyecto en Google Cloud Console**:
   ```
   https://console.cloud.google.com/
   ```

2. **Habilitar APIs necesarias**:
   - Google Sheets API
   - Google Drive API

3. **Crear Service Account**:
   - Ir a "IAM & Admin" > "Service Accounts"
   - Crear nueva cuenta de servicio
   - Descargar archivo JSON de credenciales

4. **Crear Google Sheets**:
   ```
   https://sheets.google.com/
   ```
   - Crear nueva hoja de cálculo
   - Compartir con el email del service account
   - Copiar el ID de la hoja (desde la URL)

### 1.2 Configurar Telegram Bot

1. **Crear bot con BotFather**:
   ```
   https://t.me/botfather
   ```

2. **Comandos en BotFather**:
   ```
   /newbot
   Nombre: MedConnect Bot
   Username: tu_bot_username
   ```

3. **Guardar token**:
   ```
   Token: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

## 📂 Paso 2: Preparar Repositorio GitHub

### 2.1 Crear Repositorio

1. **En GitHub**:
   - Crear nuevo repositorio público/privado
   - Nombre: `medconnect`
   - Descripción: "Sistema de Gestión Médica Familiar"

### 2.2 Subir Código

```bash
# Inicializar git (si no está inicializado)
git init

# Agregar remote origin
git remote add origin https://github.com/tu-usuario/medconnect.git

# Agregar todos los archivos
git add .

# Commit inicial
git commit -m "Initial commit: MedConnect v1.0 - Sistema completo con bot Telegram y gestión familiar"

# Subir a GitHub
git branch -M main
git push -u origin main
```

### 2.3 Verificar Archivos Subidos

**Archivos que DEBEN estar en GitHub**:
- ✅ `app.py`
- ✅ `bot.py`
- ✅ `run_bot.py`
- ✅ `config.py`
- ✅ `requirements.txt`
- ✅ `Procfile`
- ✅ `railway.json`
- ✅ `.gitignore`
- ✅ `README.md`
- ✅ Carpetas: `backend/`, `static/`, `templates/`

**Archivos que NO deben estar**:
- ❌ `*.json` (credenciales)
- ❌ `.env`
- ❌ `__pycache__/`
- ❌ `*.log`

## 🚂 Paso 3: Desplegar en Railway

### 3.1 Configurar Railway

1. **Crear cuenta**:
   ```
   https://railway.app/
   ```

2. **Conectar GitHub**:
   - "New Project" > "Deploy from GitHub repo"
   - Autorizar Railway en GitHub
   - Seleccionar repositorio `medconnect`

### 3.2 Configurar Variables de Entorno

En el dashboard de Railway, ir a "Variables" y agregar:

```bash
# Flask
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=genera-una-clave-super-segura-de-32-caracteres-minimo

# Dominio (Railway te dará uno automáticamente)
DOMAIN=tu-proyecto.up.railway.app
BASE_URL=https://tu-proyecto.up.railway.app

# Telegram
TELEGRAM_BOT_TOKEN=tu-token-completo-del-bot
TELEGRAM_BOT_ID=tu-id-de-telegram
TELEGRAM_WEBHOOK_URL=https://tu-proyecto.up.railway.app/webhook

# Google Sheets
GOOGLE_SHEETS_ID=tu-id-completo-de-google-sheets
GOOGLE_CREDENTIALS_FILE=credenciales-en-base64

# Logging
LOG_LEVEL=INFO

# Railway
PORT=5000
RAILWAY_ENVIRONMENT=production
```

### 3.3 Preparar Credenciales de Google

```bash
# En tu computadora local
base64 -i tu-archivo-credenciales.json > credenciales_base64.txt

# En Windows
certutil -encode tu-archivo-credenciales.json credenciales_base64.txt

# Copiar TODO el contenido (en una sola línea) y pegarlo en GOOGLE_CREDENTIALS_FILE
```

### 3.4 Configurar Servicios Múltiples

Railway ejecutará automáticamente:
- **Web Service**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
- **Bot Service**: `python run_bot.py`

## 🔗 Paso 4: Configurar Webhook de Telegram

### 4.1 Esperar Despliegue

Esperar que Railway termine el despliegue (2-5 minutos).

### 4.2 Configurar Webhook

```bash
# Reemplazar <TU_TOKEN> y <TU_DOMINIO>
curl -X POST "https://api.telegram.org/bot<TU_TOKEN>/setWebhook?url=https://<TU_DOMINIO>.up.railway.app/webhook"

# Ejemplo:
curl -X POST "https://api.telegram.org/bot1234567890:ABCdefGHI/setWebhook?url=https://medconnect-production.up.railway.app/webhook"
```

### 4.3 Verificar Webhook

```bash
# Verificar que el webhook esté configurado
curl "https://api.telegram.org/bot<TU_TOKEN>/getWebhookInfo"
```

## ✅ Paso 5: Verificar Funcionamiento

### 5.1 Verificar Web

1. **Acceder a la URL de Railway**:
   ```
   https://tu-proyecto.up.railway.app
   ```

2. **Verificar endpoints**:
   - `/` - Página principal
   - `/health` - Estado del servidor
   - `/webhook` - Webhook de Telegram

### 5.2 Verificar Bot

1. **Buscar tu bot en Telegram**
2. **Enviar `/start`**
3. **Probar comandos básicos**:
   - `/help`
   - `menu`
   - `familiares`

### 5.3 Verificar Google Sheets

1. **Abrir tu Google Sheets**
2. **Registrar información desde el bot**
3. **Verificar que se guarde correctamente**

## 🐛 Paso 6: Solución de Problemas

### 6.1 Errores Comunes

**Error: "Application failed to start"**
```bash
# Verificar logs en Railway
# Revisar variables de entorno
# Verificar requirements.txt
```

**Error: "Bot not responding"**
```bash
# Verificar webhook configurado
# Verificar TELEGRAM_BOT_TOKEN
# Revisar logs del bot
```

**Error: "Google Sheets access denied"**
```bash
# Verificar credenciales en base64
# Verificar permisos del service account
# Verificar GOOGLE_SHEETS_ID
```

### 6.2 Comandos de Diagnóstico

```bash
# Ver logs en Railway
railway logs

# Verificar variables de entorno
railway variables

# Redeploy si es necesario
railway deploy
```

## 🔄 Paso 7: Actualizaciones Futuras

### 7.1 Proceso de Actualización

```bash
# Hacer cambios en código local
git add .
git commit -m "Descripción de cambios"
git push origin main

# Railway redesplegará automáticamente
```

### 7.2 Monitoreo Continuo

1. **Logs de Railway**: Revisar errores
2. **Métricas de uso**: Usuarios activos
3. **Webhook status**: Estado del bot

## 📊 Paso 8: Optimización Post-Despliegue

### 8.1 Configuración de Dominio Personalizado

```bash
# En Railway, ir a Settings > Domains
# Agregar dominio personalizado
# Configurar DNS
```

### 8.2 Configuración de SSL

Railway incluye SSL automático, pero verificar:
```bash
# Verificar certificado SSL
curl -I https://tu-dominio.com
```

### 8.3 Monitoreo y Alertas

```bash
# Configurar alertas en Railway
# Monitorear uso de recursos
# Configurar backups de Google Sheets
```

## 🎯 Checklist Final

### ✅ Verificación Completa

- [ ] ✅ Código subido a GitHub sin archivos sensibles
- [ ] ✅ Railway desplegado correctamente
- [ ] ✅ Variables de entorno configuradas
- [ ] ✅ Webhook de Telegram funcionando
- [ ] ✅ Google Sheets conectado
- [ ] ✅ Bot respondiendo correctamente
- [ ] ✅ Web app funcionando
- [ ] ✅ Sistema familiar operativo
- [ ] ✅ Notificaciones funcionando
- [ ] ✅ Logs sin errores críticos

## 📞 Soporte

Si tienes problemas durante el despliegue:

1. **Revisar logs detalladamente**
2. **Verificar cada variable de entorno**
3. **Probar componentes individualmente**
4. **Consultar documentación de Railway**

## 🎉 ¡Felicitaciones!

Tu sistema MedConnect está ahora desplegado y funcionando en la nube. Los usuarios pueden:

- **Acceder a la web** desde cualquier navegador
- **Usar el bot de Telegram** desde cualquier dispositivo
- **Gestionar información familiar** de forma segura
- **Recibir notificaciones** automáticas

**¡El sistema está listo para ayudar a familias a cuidar mejor de sus seres queridos!** 🏥💙 