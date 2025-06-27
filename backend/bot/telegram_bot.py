"""
ChatBot de Telegram para MedConnect
Flujos de conversación para registro de información clínica
"""
import logging
from datetime import datetime, date
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
from backend.database.sheets_manager import sheets_db
from config import config

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Estados de conversación
MENU_PRINCIPAL, REGISTRO_USUARIO, REGISTRAR_ATENCION, REGISTRAR_MEDICAMENTO, REGISTRAR_EXAMEN = range(5)
ATENCION_FECHA, ATENCION_HORA, ATENCION_TIPO, ATENCION_ESPECIALIDAD, ATENCION_PROFESIONAL = range(5, 10)
ATENCION_CENTRO, ATENCION_DIAGNOSTICO, ATENCION_TRATAMIENTO, ATENCION_OBSERVACIONES = range(10, 14)
MEDICAMENTO_NOMBRE, MEDICAMENTO_DOSIS, MEDICAMENTO_FRECUENCIA, MEDICAMENTO_DURACION = range(14, 18)
MEDICAMENTO_INDICACIONES, MEDICAMENTO_FECHA_INICIO, MEDICAMENTO_FECHA_FIN = range(18, 21)
EXAMEN_TIPO, EXAMEN_NOMBRE, EXAMEN_FECHA_SOLICITUD, EXAMEN_FECHA_REALIZACION = range(21, 25)
EXAMEN_RESULTADO, EXAMEN_OBSERVACIONES = range(25, 27)

class MedConnectBot:
    def __init__(self):
        self.application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Configura todos los handlers del bot"""
        
        # Handler principal de conversación
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                MENU_PRINCIPAL: [
                    MessageHandler(filters.Regex('^📋 Registrar Atención$'), self.iniciar_registro_atencion),
                    MessageHandler(filters.Regex('^💊 Registrar Medicamento$'), self.iniciar_registro_medicamento),
                    MessageHandler(filters.Regex('^🔬 Registrar Examen$'), self.iniciar_registro_examen),
                    MessageHandler(filters.Regex('^📊 Ver Mi Historial$'), self.ver_historial),
                    MessageHandler(filters.Regex('^👨‍👩‍👧‍👦 Gestionar Familiares$'), self.gestionar_familiares),
                    MessageHandler(filters.Regex('^⚙️ Configuración$'), self.configuracion),
                    MessageHandler(filters.Regex('^ℹ️ Ayuda$'), self.ayuda),
                ],
                REGISTRO_USUARIO: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.procesar_registro_usuario)
                ],
                # Estados para registro de atención
                ATENCION_FECHA: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.atencion_fecha)],
                ATENCION_HORA: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.atencion_hora)],
                ATENCION_TIPO: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.atencion_tipo)],
                ATENCION_ESPECIALIDAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.atencion_especialidad)],
                ATENCION_PROFESIONAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.atencion_profesional)],
                ATENCION_CENTRO: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.atencion_centro)],
                ATENCION_DIAGNOSTICO: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.atencion_diagnostico)],
                ATENCION_TRATAMIENTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.atencion_tratamiento)],
                ATENCION_OBSERVACIONES: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.atencion_observaciones)],
                # Estados para medicamentos
                MEDICAMENTO_NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.medicamento_nombre)],
                MEDICAMENTO_DOSIS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.medicamento_dosis)],
                MEDICAMENTO_FRECUENCIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.medicamento_frecuencia)],
                MEDICAMENTO_DURACION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.medicamento_duracion)],
                MEDICAMENTO_INDICACIONES: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.medicamento_indicaciones)],
                MEDICAMENTO_FECHA_INICIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.medicamento_fecha_inicio)],
                MEDICAMENTO_FECHA_FIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.medicamento_fecha_fin)],
                # Estados para exámenes
                EXAMEN_TIPO: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.examen_tipo)],
                EXAMEN_NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.examen_nombre)],
                EXAMEN_FECHA_SOLICITUD: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.examen_fecha_solicitud)],
                EXAMEN_FECHA_REALIZACION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.examen_fecha_realizacion)],
                EXAMEN_RESULTADO: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.examen_resultado)],
                EXAMEN_OBSERVACIONES: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.examen_observaciones)],
            },
            fallbacks=[
                CommandHandler('cancel', self.cancel),
                CommandHandler('menu', self.menu_principal),
                MessageHandler(filters.Regex('^🏠 Menú Principal$'), self.menu_principal)
            ]
        )
        
        self.application.add_handler(conv_handler)
        self.application.add_handler(CommandHandler('help', self.ayuda))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
    
    def get_main_keyboard(self):
        """Teclado principal del menú"""
        keyboard = [
            ['📋 Registrar Atención', '💊 Registrar Medicamento'],
            ['🔬 Registrar Examen', '📊 Ver Mi Historial'],
            ['👨‍👩‍👧‍👦 Gestionar Familiares', '⚙️ Configuración'],
            ['ℹ️ Ayuda']
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    def get_cancel_keyboard(self):
        """Teclado para cancelar"""
        keyboard = [['🏠 Menú Principal', '❌ Cancelar']]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        user = update.effective_user
        telegram_id = str(user.id)
        
        # Verificar si el usuario ya está registrado
        existing_user = sheets_db.get_user_by_telegram_id(telegram_id)
        
        if existing_user:
            await update.message.reply_text(
                f"¡Hola de nuevo, {existing_user.get('nombre', 'Usuario')}! 👋\n\n"
                f"Bienvenido/a a MedConnect, tu asistente personal de salud.\n"
                f"¿En qué puedo ayudarte hoy?",
                reply_markup=self.get_main_keyboard()
            )
            return MENU_PRINCIPAL
        else:
            await update.message.reply_text(
                f"¡Hola {user.first_name}! 👋 Bienvenido/a a MedConnect.\n\n"
                f"Soy tu asistente personal de salud y te ayudaré a registrar y gestionar "
                f"tu información clínica de manera fácil y segura.\n\n"
                f"Antes de comenzar, necesito registrar algunos datos básicos.\n"
                f"Por favor, escribe tu nombre completo:"
            )
            # Inicializar datos del usuario en el contexto
            context.user_data['registro'] = {'telegram_id': telegram_id}
            context.user_data['paso_registro'] = 'nombre'
            return REGISTRO_USUARIO
    
    async def procesar_registro_usuario(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa el registro paso a paso del usuario"""
        text = update.message.text.strip()
        paso = context.user_data.get('paso_registro', 'nombre')
        
        if paso == 'nombre':
            # Dividir nombre y apellido
            nombres = text.split()
            if len(nombres) >= 2:
                context.user_data['registro']['nombre'] = ' '.join(nombres[:-1])
                context.user_data['registro']['apellido'] = nombres[-1]
            else:
                context.user_data['registro']['nombre'] = text
                context.user_data['registro']['apellido'] = ''
            
            context.user_data['paso_registro'] = 'edad'
            await update.message.reply_text(
                "Perfecto! 👍\n\n"
                "Ahora, por favor dime tu edad:"
            )
            return REGISTRO_USUARIO
            
        elif paso == 'edad':
            try:
                edad = int(text)
                if 18 <= edad <= 120:
                    context.user_data['registro']['edad'] = edad
                    context.user_data['paso_registro'] = 'telefono'
                    await update.message.reply_text(
                        "Excelente! 📱\n\n"
                        "Por favor, comparte tu número de teléfono (incluye el código de país si es necesario):"
                    )
                    return REGISTRO_USUARIO
                else:
                    await update.message.reply_text(
                        "Por favor ingresa una edad válida (entre 18 y 120 años):"
                    )
                    return REGISTRO_USUARIO
            except ValueError:
                await update.message.reply_text(
                    "Por favor ingresa tu edad como un número:"
                )
                return REGISTRO_USUARIO
                
        elif paso == 'telefono':
            context.user_data['registro']['telefono'] = text
            context.user_data['paso_registro'] = 'email'
            await update.message.reply_text(
                "Genial! 📧\n\n"
                "Ahora tu correo electrónico (opcional, puedes escribir 'no' para omitir):"
            )
            return REGISTRO_USUARIO
            
        elif paso == 'email':
            if text.lower() != 'no':
                context.user_data['registro']['email'] = text
            else:
                context.user_data['registro']['email'] = ''
            
            # Crear usuario en la base de datos
            try:
                user_id = sheets_db.create_user(context.user_data['registro'])
                
                # Log de registro exitoso
                sheets_db.log_action(
                    user_id, 
                    'registro', 
                    'Usuario registrado exitosamente', 
                    result='success'
                )
                
                nombre = context.user_data['registro']['nombre']
                await update.message.reply_text(
                    f"¡Registro completado exitosamente, {nombre}! ✅\n\n"
                    f"Ya puedes comenzar a usar MedConnect para gestionar tu información clínica.\n\n"
                    f"¿Qué te gustaría hacer?",
                    reply_markup=self.get_main_keyboard()
                )
                
                # Limpiar datos temporales
                context.user_data.clear()
                return MENU_PRINCIPAL
                
            except Exception as e:
                logger.error(f"Error registrando usuario: {e}")
                await update.message.reply_text(
                    "❌ Hubo un error al registrar tus datos. Por favor, intenta nuevamente más tarde.\n\n"
                    "Si el problema persiste, contacta al soporte."
                )
                return ConversationHandler.END
    
    async def menu_principal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el menú principal"""
        await update.message.reply_text(
            "🏠 Menú Principal\n\n"
            "¿Qué te gustaría hacer?",
            reply_markup=self.get_main_keyboard()
        )
        return MENU_PRINCIPAL
    
    # Flujo de registro de atención médica
    async def iniciar_registro_atencion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Inicia el flujo de registro de atención médica"""
        context.user_data['atencion'] = {}
        await update.message.reply_text(
            "📋 Registro de Atención Médica\n\n"
            "Te guiaré paso a paso para registrar tu atención médica.\n\n"
            "¿En qué fecha fue tu atención? (DD/MM/AAAA)\n"
            "Por ejemplo: 25/04/2024",
            reply_markup=self.get_cancel_keyboard()
        )
        return ATENCION_FECHA
    
    async def atencion_fecha(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa la fecha de la atención"""
        text = update.message.text.strip()
        
        if text in ['🏠 Menú Principal', '❌ Cancelar']:
            return await self.menu_principal(update, context)
        
        try:
            # Validar formato de fecha
            fecha_obj = datetime.strptime(text, '%d/%m/%Y')
            context.user_data['atencion']['fecha'] = fecha_obj.strftime('%Y-%m-%d')
            
            await update.message.reply_text(
                "Perfecto! 🕐\n\n"
                "¿A qué hora fue tu atención? (HH:MM)\n"
                "Por ejemplo: 14:30"
            )
            return ATENCION_HORA
            
        except ValueError:
            await update.message.reply_text(
                "❌ Formato de fecha incorrecto.\n\n"
                "Por favor usa el formato DD/MM/AAAA\n"
                "Ejemplo: 25/04/2024"
            )
            return ATENCION_FECHA
    
    async def atencion_hora(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa la hora de la atención"""
        text = update.message.text.strip()
        
        if text in ['🏠 Menú Principal', '❌ Cancelar']:
            return await self.menu_principal(update, context)
        
        try:
            # Validar formato de hora
            datetime.strptime(text, '%H:%M')
            context.user_data['atencion']['hora'] = text
            
            # Ofrecer tipos de atención
            keyboard = [
                ['🏥 Consulta Médica', '🚑 Urgencia'],
                ['🔄 Control', '💉 Procedimiento'],
                ['🩺 Examen', '🏠 Atención Domiciliaria'],
                ['🏠 Menú Principal']
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                "Excelente! 🏥\n\n"
                "¿Qué tipo de atención recibiste?",
                reply_markup=reply_markup
            )
            return ATENCION_TIPO
            
        except ValueError:
            await update.message.reply_text(
                "❌ Formato de hora incorrecto.\n\n"
                "Por favor usa el formato HH:MM\n"
                "Ejemplo: 14:30"
            )
            return ATENCION_HORA
    
    async def atencion_tipo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa el tipo de atención"""
        text = update.message.text.strip()
        
        if text == '🏠 Menú Principal':
            return await self.menu_principal(update, context)
        
        # Mapear emojis a tipos
        tipos_map = {
            '🏥 Consulta Médica': 'Consulta Médica',
            '🚑 Urgencia': 'Urgencia',
            '🔄 Control': 'Control',
            '💉 Procedimiento': 'Procedimiento',
            '🩺 Examen': 'Examen',
            '🏠 Atención Domiciliaria': 'Atención Domiciliaria'
        }
        
        tipo_atencion = tipos_map.get(text, text)
        context.user_data['atencion']['tipo_atencion'] = tipo_atencion
        
        # Ofrecer especialidades
        keyboard = [
            ['👨‍⚕️ Medicina General', '❤️ Cardiología'],
            ['🦴 Traumatología', '🧠 Neurología'],
            ['👁️ Oftalmología', '👂 Otorrinolaringología'],
            ['🫁 Neumología', '🍎 Nutrición'],
            ['🧘‍♀️ Kinesiología', '🧠 Psicología'],
            ['🏠 Menú Principal']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "Perfecto! 👨‍⚕️\n\n"
            "¿Cuál fue la especialidad médica?",
            reply_markup=reply_markup
        )
        return ATENCION_ESPECIALIDAD
    
    async def atencion_especialidad(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa la especialidad de la atención"""
        text = update.message.text.strip()
        
        if text == '🏠 Menú Principal':
            return await self.menu_principal(update, context)
        
        # Mapear emojis a especialidades
        especialidades_map = {
            '👨‍⚕️ Medicina General': 'Medicina General',
            '❤️ Cardiología': 'Cardiología',
            '🦴 Traumatología': 'Traumatología',
            '🧠 Neurología': 'Neurología',
            '👁️ Oftalmología': 'Oftalmología',
            '👂 Otorrinolaringología': 'Otorrinolaringología',
            '🫁 Neumología': 'Neumología',
            '🍎 Nutrición': 'Nutrición',
            '🧘‍♀️ Kinesiología': 'Kinesiología',
            '🧠 Psicología': 'Psicología'
        }
        
        especialidad = especialidades_map.get(text, text)
        context.user_data['atencion']['especialidad'] = especialidad
        
        await update.message.reply_text(
            "Excelente! 👨‍⚕️\n\n"
            "¿Cuál es el nombre del profesional que te atendió?\n"
            "(Por ejemplo: Dr. Juan Pérez)",
            reply_markup=self.get_cancel_keyboard()
        )
        return ATENCION_PROFESIONAL
    
    async def atencion_profesional(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa el nombre del profesional"""
        text = update.message.text.strip()
        
        if text in ['🏠 Menú Principal', '❌ Cancelar']:
            return await self.menu_principal(update, context)
        
        context.user_data['atencion']['profesional'] = text
        
        await update.message.reply_text(
            "Perfecto! 🏥\n\n"
            "¿En qué centro de salud o clínica fue la atención?\n"
            "(Por ejemplo: Hospital Público, Clínica Santa María, CESFAM Norte)"
        )
        return ATENCION_CENTRO
    
    async def atencion_centro(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa el centro de salud"""
        text = update.message.text.strip()
        
        if text in ['🏠 Menú Principal', '❌ Cancelar']:
            return await self.menu_principal(update, context)
        
        context.user_data['atencion']['centro_salud'] = text
        
        await update.message.reply_text(
            "Genial! 📋\n\n"
            "¿Cuál fue el diagnóstico o motivo de consulta?\n"
            "(Describe brevemente lo que te dijeron)"
        )
        return ATENCION_DIAGNOSTICO
    
    async def atencion_diagnostico(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa el diagnóstico"""
        text = update.message.text.strip()
        
        if text in ['🏠 Menú Principal', '❌ Cancelar']:
            return await self.menu_principal(update, context)
        
        context.user_data['atencion']['diagnostico'] = text
        
        await update.message.reply_text(
            "Excelente! 💊\n\n"
            "¿Qué tratamiento o indicaciones te dieron?\n"
            "(Por ejemplo: medicamentos, terapias, cambios de hábitos)\n\n"
            "Si no hubo tratamiento específico, puedes escribir 'ninguno'"
        )
        return ATENCION_TRATAMIENTO
    
    async def atencion_tratamiento(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa el tratamiento"""
        text = update.message.text.strip()
        
        if text in ['🏠 Menú Principal', '❌ Cancelar']:
            return await self.menu_principal(update, context)
        
        context.user_data['atencion']['tratamiento'] = text if text.lower() != 'ninguno' else ''
        
        await update.message.reply_text(
            "Perfecto! 📝\n\n"
            "¿Hay alguna observación adicional que quieras agregar?\n"
            "(Opcional - puedes escribir 'no' para omitir)"
        )
        return ATENCION_OBSERVACIONES
    
    async def atencion_observaciones(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa las observaciones y guarda la atención"""
        text = update.message.text.strip()
        
        if text in ['🏠 Menú Principal', '❌ Cancelar']:
            return await self.menu_principal(update, context)
        
        # Agregar observaciones
        context.user_data['atencion']['observaciones'] = text if text.lower() != 'no' else ''
        
        # Obtener usuario
        telegram_id = str(update.effective_user.id)
        user = sheets_db.get_user_by_telegram_id(telegram_id)
        
        if not user:
            await update.message.reply_text(
                "❌ Error: No se pudo encontrar tu perfil de usuario.\n"
                "Por favor, reinicia el bot con /start"
            )
            return ConversationHandler.END
        
        # Agregar user_id a los datos de la atención
        context.user_data['atencion']['user_id'] = user['user_id']
        
        try:
            # Guardar en Google Sheets
            atencion_id = sheets_db.create_atencion(context.user_data['atencion'])
            
            # Log de la acción
            sheets_db.log_action(
                user['user_id'],
                'registro_atencion',
                f'Atención registrada: {atencion_id}',
                result='success'
            )
            
            # Crear resumen para el usuario
            atencion = context.user_data['atencion']
            resumen = (
                f"✅ ¡Atención registrada exitosamente!\n\n"
                f"📅 Fecha: {atencion['fecha']}\n"
                f"🕐 Hora: {atencion['hora']}\n"
                f"🏥 Tipo: {atencion['tipo_atencion']}\n"
                f"👨‍⚕️ Especialidad: {atencion['especialidad']}\n"
                f"🩺 Profesional: {atencion['profesional']}\n"
                f"🏥 Centro: {atencion['centro_salud']}\n"
                f"📋 Diagnóstico: {atencion['diagnostico']}\n"
            )
            
            if atencion.get('tratamiento'):
                resumen += f"💊 Tratamiento: {atencion['tratamiento']}\n"
            
            if atencion.get('observaciones'):
                resumen += f"📝 Observaciones: {atencion['observaciones']}\n"
            
            resumen += f"\n🆔 ID de registro: {atencion_id}"
            
            await update.message.reply_text(
                resumen,
                reply_markup=self.get_main_keyboard()
            )
            
            # Limpiar datos temporales
            context.user_data.pop('atencion', None)
            return MENU_PRINCIPAL
            
        except Exception as e:
            logger.error(f"Error guardando atención: {e}")
            await update.message.reply_text(
                "❌ Hubo un error al guardar la atención médica.\n"
                "Por favor, intenta nuevamente más tarde.",
                reply_markup=self.get_main_keyboard()
            )
            return MENU_PRINCIPAL
    
    async def ver_historial(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el historial del usuario"""
        telegram_id = str(update.effective_user.id)
        
        try:
            resumen = sheets_db.get_user_summary(telegram_id)
            
            if not resumen:
                await update.message.reply_text(
                    "❌ No se pudo cargar tu historial.\n"
                    "Asegúrate de estar registrado con /start"
                )
                return MENU_PRINCIPAL
            
            usuario = resumen['usuario']
            nombre = usuario.get('nombre', 'Usuario')
            
            # Crear mensaje de historial
            mensaje = f"📊 Historial Médico - {nombre}\n\n"
            
            # Estadísticas generales
            mensaje += f"📈 Resumen:\n"
            mensaje += f"• Total de atenciones: {resumen['total_atenciones']}\n"
            mensaje += f"• Medicamentos activos: {resumen['medicamentos_activos']}\n"
            mensaje += f"• Familiares autorizados: {resumen['familiares_autorizados']}\n\n"
            
            # Atenciones recientes
            if resumen['atenciones_recientes']:
                mensaje += f"🏥 Últimas 3 atenciones:\n"
                for atencion in resumen['atenciones_recientes'][:3]:
                    fecha = atencion.get('fecha', 'Sin fecha')
                    especialidad = atencion.get('especialidad', 'Sin especialidad')
                    profesional = atencion.get('profesional', 'Sin profesional')
                    mensaje += f"• {fecha} - {especialidad} ({profesional})\n"
                mensaje += "\n"
            
            # Medicamentos activos
            if resumen['medicamentos']:
                mensaje += f"💊 Medicamentos activos:\n"
                for med in resumen['medicamentos'][:3]:
                    nombre_med = med.get('nombre_medicamento', 'Sin nombre')
                    dosis = med.get('dosis', 'Sin dosis')
                    frecuencia = med.get('frecuencia', 'Sin frecuencia')
                    mensaje += f"• {nombre_med} - {dosis} - {frecuencia}\n"
                
                if len(resumen['medicamentos']) > 3:
                    mensaje += f"• ... y {len(resumen['medicamentos']) - 3} más\n"
            
            await update.message.reply_text(mensaje)
            
        except Exception as e:
            logger.error(f"Error obteniendo historial: {e}")
            await update.message.reply_text(
                "❌ Error al cargar el historial.\n"
                "Por favor, intenta más tarde."
            )
        
        return MENU_PRINCIPAL
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancela la conversación actual"""
        await update.message.reply_text(
            "❌ Operación cancelada.\n\n"
            "¿En qué más puedo ayudarte?",
            reply_markup=self.get_main_keyboard()
        )
        return MENU_PRINCIPAL
    
    async def ayuda(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra la ayuda del bot"""
        help_text = """
🤖 **MedConnect Bot - Guía de Uso**

**Funciones principales:**
📋 **Registrar Atención** - Registra tus consultas médicas
💊 **Registrar Medicamento** - Guarda información de medicamentos
🔬 **Registrar Examen** - Registra exámenes y resultados
📊 **Ver Historial** - Consulta tu historial médico
👨‍👩‍👧‍👦 **Familiares** - Gestiona acceso familiar

**Comandos útiles:**
/start - Iniciar o reiniciar el bot
/menu - Ir al menú principal
/help - Mostrar esta ayuda
/cancel - Cancelar operación actual

**Consejos:**
• Usa el teclado de botones para navegar
• Siempre puedes cancelar con /cancel
• Tu información se guarda de forma segura
• Los familiares autorizados pueden ver tu historial

**Soporte:**
Si tienes problemas, contacta al equipo de MedConnect.
        """
        
        await update.message.reply_text(help_text)
        return MENU_PRINCIPAL
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja los callbacks de botones inline"""
        query = update.callback_query
        await query.answer()
        
        # Aquí puedes manejar diferentes callbacks
        # Por ejemplo, para confirmaciones, navegación, etc.
        
        return MENU_PRINCIPAL
    
    def run(self):
        """Ejecuta el bot"""
        logger.info("Iniciando MedConnect Bot...")
        self.application.run_polling()

# Función para inicializar el bot
def main():
    bot = MedConnectBot()
    bot.run()

if __name__ == '__main__':
    main() 