# 👨‍👩‍👧‍👦 Sistema de Gestión Familiar - MedConnect Bot

## 🎯 Funcionalidad Implementada

El bot MedConnect ahora incluye un **sistema completo de gestión familiar** que permite a los familiares acceder y gestionar la información médica de otros miembros de la familia, especialmente útil para cuidar a personas de la tercera edad.

## 📋 Características Principales

### 1. **Autorización de Familiares**
- ✅ Proceso guiado paso a paso para autorizar familiares
- ✅ Diferentes niveles de permisos (Lectura, Escritura, Admin)
- ✅ Registro de parentesco y datos de contacto
- ✅ Vinculación con Telegram ID para notificaciones

### 2. **Gestión de Permisos**
- 👀 **Solo Ver**: Puede consultar información médica
- ✏️ **Ver y Editar**: Puede ver y agregar nueva información
- 👑 **Control Total**: Puede gestionar todo (ideal para cuidadores)

### 3. **Sistema de Notificaciones Automáticas**
- 🔔 Notificaciones cuando el usuario principal usa el bot
- 📱 Avisos de nuevas consultas médicas registradas
- 💊 Recordatorios de medicamentos a familiares
- 🏥 Alertas de citas médicas próximas

### 4. **Gestión Multi-Usuario**
- 🔄 Cambio entre gestión propia y de familiares
- 👥 Vista de todos los usuarios que puede gestionar
- 📊 Acceso a información médica completa de familiares autorizados

## 🚀 Cómo Usar el Sistema

### **Para Autorizar un Familiar:**

1. **Iniciar proceso**: Escribir `familiares` o usar el menú
2. **Seleccionar**: "👤 Autorizar Familiar"
3. **Completar datos**:
   - Nombre completo del familiar
   - Parentesco (hijo, hija, esposo, etc.)
   - Número de teléfono
   - Nivel de permisos
   - Telegram ID (opcional, para notificaciones)

### **Para Gestionar Información de un Familiar:**

1. **Acceder**: Menú "🔄 Cambiar Usuario Gestionado"
2. **Seleccionar**: El familiar que quieres gestionar
3. **Usar normalmente**: Todas las funciones del bot ahora aplican al familiar
4. **Volver**: Comando `/mi_info` para regresar a tu información

### **Para Configurar Recordatorios:**

1. **Acceder**: Escribir `notificaciones` o `recordatorios`
2. **Seleccionar tipo**:
   - 💊 Medicamento
   - 🏥 Cita Médica  
   - 📋 Recordatorio General
3. **Configurar**: Hora, frecuencia, notificaciones a familia

## 💡 Casos de Uso Prácticos

### **Ejemplo: Familia con Madre de Tercera Edad**

**Configuración Inicial:**
```
Madre (85 años) autoriza a:
- Hijo 1: Permisos de "Control Total"
- Hijo 2: Permisos de "Ver y Editar" 
- Hijo 3: Permisos de "Solo Ver"
```

**Flujo de Uso:**

1. **Hijo 1 registra consulta médica de la madre**:
   - Cambia a gestionar información de la madre
   - Registra: "28/11/2025, 10:30, Cardiología, Dr. González, Hospital Central, Control de presión arterial"
   - Automáticamente se notifica a Hijo 2 e Hijo 3

2. **Configuración de recordatorios**:
   - Hijo 1 programa: "Medicamento: Losartán, 08:00, Diario"
   - Todos los hijos reciben notificación diaria

3. **Madre usa el bot**:
   - Cuando la madre envía cualquier mensaje
   - Los hijos reciben: "🔔 Mamá está usando MedConnect - 15:30"

4. **Acceso a información**:
   - Cualquier hijo puede ver historial médico completo
   - Solo Hijo 1 e Hijo 2 pueden agregar información
   - Hijo 3 solo puede consultar

## 🔧 Comandos y Funciones

### **Comandos Especiales:**
- `/mi_info` - Volver a tu información personal
- `/familiares` - Gestión familiar
- `/notificaciones` - Recordatorios y avisos
- `/help` - Ayuda completa

### **Palabras Clave:**
- `familiares` - Menú de gestión familiar
- `notificaciones` - Sistema de recordatorios
- `gestionar [nombre]` - Cambiar usuario gestionado
- `menu` - Menú principal

## 📊 Estructura de Datos

### **Tabla: Familiares_Autorizados**
```
- familiar_id: ID único del familiar
- user_id: ID del usuario principal
- nombre_familiar: Nombre completo
- parentesco: Relación familiar
- telefono: Número de contacto
- email: Correo electrónico
- telegram_id: ID de Telegram (para notificaciones)
- permisos: lectura/escritura/admin
- fecha_autorizacion: Cuándo fue autorizado
- estado: activo/inactivo
- notificaciones: true/false
```

### **Tabla: Recordatorios**
```
- reminder_id: ID único del recordatorio
- user_id: Usuario objetivo
- tipo: medicamento/cita/general
- titulo: Título del recordatorio
- mensaje: Mensaje completo
- fecha_programada: Cuándo activar
- hora_programada: Hora específica
- frecuencia: unica/diaria/semanal
- notificar_familiares: true/false
- estado: activo/inactivo
```

## 🛡️ Seguridad y Privacidad

### **Control de Acceso:**
- ✅ Verificación de permisos en cada operación
- ✅ Logs de todas las acciones familiares
- ✅ Autorización explícita requerida
- ✅ Revocación de permisos disponible

### **Notificaciones Seguras:**
- 🔐 Solo familiares autorizados reciben notificaciones
- 📱 Telegram ID verificado antes de enviar
- ⏰ Timestamps en todas las notificaciones
- 🚫 Opción de desactivar notificaciones

## 📈 Beneficios del Sistema

1. **Para Personas Mayores:**
   - No necesitan recordar comandos complejos
   - Familiares pueden ayudar con registro de información
   - Seguimiento automático de medicamentos

2. **Para Familiares Cuidadores:**
   - Acceso completo a información médica
   - Notificaciones automáticas de actividad
   - Capacidad de programar recordatorios

3. **Para Toda la Familia:**
   - Transparencia en el cuidado médico
   - Coordinación entre múltiples cuidadores
   - Historial médico centralizado y accesible

## 🔄 Flujo de Notificaciones

### **Notificaciones Automáticas:**

```
Evento: Usuario principal envía mensaje
↓
Sistema verifica familiares autorizados
↓
Envía notificación: "🔔 [Nombre] está usando MedConnect - [Hora]"
↓
Familiares reciben alerta en tiempo real
```

### **Recordatorios Programados:**

```
Recordatorio de medicamento programado
↓
Sistema verifica hora y frecuencia
↓
Envía a usuario principal: "💊 Es hora de tomar [Medicamento]"
↓
Si está configurado, notifica a familiares
↓
Familiares reciben: "🔔 [Nombre] debe tomar [Medicamento]"
```

## ✅ Estado de Implementación

- ✅ **Autorización de familiares**: Completado
- ✅ **Sistema de permisos**: Completado  
- ✅ **Gestión multi-usuario**: Completado
- ✅ **Notificaciones básicas**: Completado
- ✅ **Recordatorios**: Completado
- ✅ **Interfaz de usuario**: Completado
- ✅ **Base de datos**: Completado

## 🎯 Resultado Final

El sistema de gestión familiar de MedConnect permite que una familia completa pueda cuidar colaborativamente de un miembro, especialmente personas de la tercera edad, con:

- **Control total** de información médica
- **Notificaciones automáticas** de actividad
- **Recordatorios inteligentes** de medicamentos y citas
- **Interfaz simple** y accesible para todos los niveles técnicos
- **Seguridad robusta** con control de permisos

¡La familia ahora puede estar siempre conectada y cuidar mejor de sus seres queridos! 👨‍👩‍👧‍👦💙 