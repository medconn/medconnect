"""
Handlers adicionales para el ChatBot de MedConnect
Flujos de medicamentos, exámenes y gestión familiar
"""
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from backend.database.sheets_manager import sheets_db
import logging

logger = logging.getLogger(__name__)

class BotHandlers:
    """Clase con handlers adicionales para el bot"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
    
    # === FLUJOS DE MEDICAMENTOS ===
    
    async def iniciar_registro_medicamento(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Inicia el flujo de registro de medicamento"""
        context.user_data['medicamento'] = {}
        await update.message.reply_text(
            "💊 Registro de Medicamento\n\n"
            "Te ayudaré a registrar un medicamento paso a paso.\n\n"
            "¿Cuál es el nombre del medicamento?\n"
            "(Por ejemplo: Atorvastatina, Losartán, Metformina)",
            reply_markup=self.bot.get_cancel_keyboard()
        )
        return self.bot.MEDICAMENTO_NOMBRE
    
    async def medicamento_nombre(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa el nombre del medicamento"""
        text = update.message.text.strip()
        
        if text in ['🏠 Menú Principal', '❌ Cancelar']:
            return await self.bot.menu_principal(update, context)
        
        context.user_data['medicamento']['nombre_medicamento'] = text
        
        await update.message.reply_text(
            f"Perfecto! 💊\n\n"
            f"Medicamento: {text}\n\n"
            f"¿Cuál es la dosis?\n"
            f"(Por ejemplo: 20mg, 1 comprimido, 5ml)"
        )
        return self.bot.MEDICAMENTO_DOSIS
    
    async def medicamento_dosis(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa la dosis del medicamento"""
        text = update.message.text.strip()
        
        if text in ['🏠 Menú Principal', '❌ Cancelar']:
            return await self.bot.menu_principal(update, context)
        
        context.user_data['medicamento']['dosis'] = text
        
        # Ofrecer frecuencias comunes
        keyboard = [
            ['📅 Una vez al día', '📅 Dos veces al día'],
            ['📅 Tres veces al día', '📅 Cada 8 horas'],
            ['📅 Cada 12 horas', '📅 Según necesidad'],
            ['✏️ Escribir otra frecuencia', '🏠 Menú Principal']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            f"Excelente! ⏰\n\n"
            f"¿Con qué frecuencia debes tomarlo?",
            reply_markup=reply_markup
        )
        return self.bot.MEDICAMENTO_FRECUENCIA
    
    async def medicamento_frecuencia(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa la frecuencia del medicamento"""
        text = update.message.text.strip()
        
        if text == '🏠 Menú Principal':
            return await self.bot.menu_principal(update, context)
        
        # Mapear frecuencias comunes
        frecuencias_map = {
            '📅 Una vez al día': 'Una vez al día',
            '📅 Dos veces al día': 'Dos veces al día',
            '📅 Tres veces al día': 'Tres veces al día',
            '📅 Cada 8 horas': 'Cada 8 horas',
            '📅 Cada 12 horas': 'Cada 12 horas',
            '📅 Según necesidad': 'Según necesidad'
        }
        
        if text == '✏️ Escribir otra frecuencia':
            await update.message.reply_text(
                "Por favor, escribe la frecuencia del medicamento:\n"
                "(Por ejemplo: Cada 6 horas, Una vez por semana)"
            )
            return self.bot.MEDICAMENTO_FRECUENCIA
        
        frecuencia = frecuencias_map.get(text, text)
        context.user_data['medicamento']['frecuencia'] = frecuencia
        
        # Ofrecer duraciones comunes
        keyboard = [
            ['📆 7 días', '📆 15 días'],
            ['📆 30 días', '📆 60 días'],
            ['📆 90 días', '📆 Tratamiento continuo'],
            ['✏️ Escribir otra duración', '🏠 Menú Principal']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            f"Perfecto! 📅\n\n"
            f"¿Por cuánto tiempo debes tomarlo?",
            reply_markup=reply_markup
        )
        return self.bot.MEDICAMENTO_DURACION
    
    async def medicamento_duracion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa la duración del medicamento"""
        text = update.message.text.strip()
        
        if text == '🏠 Menú Principal':
            return await self.bot.menu_principal(update, context)
        
        duraciones_map = {
            '📆 7 días': '7 días',
            '📆 15 días': '15 días',
            '📆 30 días': '30 días',
            '📆 60 días': '60 días',
            '📆 90 días': '90 días',
            '📆 Tratamiento continuo': 'Continuo'
        }
        
        if text == '✏️ Escribir otra duración':
            await update.message.reply_text(
                "Por favor, escribe la duración del tratamiento:\n"
                "(Por ejemplo: 21 días, 6 meses, hasta nueva indicación)"
            )
            return self.bot.MEDICAMENTO_DURACION
        
        duracion = duraciones_map.get(text, text)
        context.user_data['medicamento']['duracion'] = duracion
        
        await update.message.reply_text(
            f"Genial! 📝\n\n"
            f"¿Hay indicaciones especiales para este medicamento?\n"
            f"(Por ejemplo: Tomar con comida, en ayunas, antes de dormir)\n\n"
            f"Si no hay indicaciones especiales, puedes escribir 'no'",
            reply_markup=self.bot.get_cancel_keyboard()
        )
        return self.bot.MEDICAMENTO_INDICACIONES
    
    async def medicamento_indicaciones(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa las indicaciones del medicamento"""
        text = update.message.text.strip()
        
        if text in ['🏠 Menú Principal', '❌ Cancelar']:
            return await self.bot.menu_principal(update, context)
        
        context.user_data['medicamento']['indicaciones'] = text if text.lower() != 'no' else ''
        
        await update.message.reply_text(
            f"Excelente! 📅\n\n"
            f"¿Cuándo comenzaste a tomar este medicamento? (DD/MM/AAAA)\n"
            f"Si es hoy, puedes escribir 'hoy'"
        )
        return self.bot.MEDICAMENTO_FECHA_INICIO
    
    async def medicamento_fecha_inicio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa la fecha de inicio del medicamento"""
        text = update.message.text.strip()
        
        if text in ['🏠 Menú Principal', '❌ Cancelar']:
            return await self.bot.menu_principal(update, context)
        
        try:
            if text.lower() == 'hoy':
                fecha_inicio = datetime.now().strftime('%Y-%m-%d')
            else:
                fecha_obj = datetime.strptime(text, '%d/%m/%Y')
                fecha_inicio = fecha_obj.strftime('%Y-%m-%d')
            
            context.user_data['medicamento']['fecha_inicio'] = fecha_inicio
            
            # Calcular fecha fin basada en la duración
            duracion = context.user_data['medicamento']['duracion']
            
            if duracion == 'Continuo':
                await update.message.reply_text(
                    f"Perfecto! ✅\n\n"
                    f"Como es un tratamiento continuo, no necesito fecha de fin.\n\n"
                    f"¿Quieres agregar alguna observación adicional?\n"
                    f"(Opcional - puedes escribir 'no' para omitir)"
                )
                # Establecer fecha fin muy lejana para tratamiento continuo
                context.user_data['medicamento']['fecha_fin'] = '2099-12-31'
                return self.bot.MEDICAMENTO_FECHA_FIN  # Reutilizamos para observaciones
            else:
                await update.message.reply_text(
                    f"Perfecto! 📅\n\n"
                    f"¿Hasta qué fecha debes tomarlo? (DD/MM/AAAA)\n"
                    f"O puedes escribir 'calcular' para que lo calcule automáticamente"
                )
                return self.bot.MEDICAMENTO_FECHA_FIN
                
        except ValueError:
            await update.message.reply_text(
                "❌ Formato de fecha incorrecto.\n\n"
                "Por favor usa el formato DD/MM/AAAA o escribe 'hoy'"
            )
            return self.bot.MEDICAMENTO_FECHA_INICIO
    
    async def medicamento_fecha_fin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa la fecha de fin del medicamento y guarda el registro"""
        text = update.message.text.strip()
        
        if text in ['🏠 Menú Principal', '❌ Cancelar']:
            return await self.bot.menu_principal(update, context)
        
        # Si ya tenemos fecha_fin (tratamiento continuo), este es para observaciones
        if 'fecha_fin' in context.user_data['medicamento']:
            context.user_data['medicamento']['observaciones'] = text if text.lower() != 'no' else ''
        else:
            # Procesar fecha fin
            try:
                if text.lower() == 'calcular':
                    # Calcular automáticamente (funcionalidad básica)
                    fecha_inicio = datetime.strptime(context.user_data['medicamento']['fecha_inicio'], '%Y-%m-%d')
                    duracion = context.user_data['medicamento']['duracion']
                    
                    # Extraer número de días
                    if 'días' in duracion:
                        dias = int(duracion.split()[0])
                        fecha_fin = fecha_inicio + timedelta(days=dias)
                        context.user_data['medicamento']['fecha_fin'] = fecha_fin.strftime('%Y-%m-%d')
                    else:
                        # Por defecto 30 días si no se puede calcular
                        fecha_fin = fecha_inicio + timedelta(days=30)
                        context.user_data['medicamento']['fecha_fin'] = fecha_fin.strftime('%Y-%m-%d')
                else:
                    fecha_obj = datetime.strptime(text, '%d/%m/%Y')
                    context.user_data['medicamento']['fecha_fin'] = fecha_obj.strftime('%Y-%m-%d')
                
            except ValueError:
                await update.message.reply_text(
                    "❌ Formato de fecha incorrecto.\n\n"
                    "Por favor usa el formato DD/MM/AAAA o escribe 'calcular'"
                )
                return self.bot.MEDICAMENTO_FECHA_FIN
        
        # Obtener usuario y guardar medicamento
        telegram_id = str(update.effective_user.id)
        user = sheets_db.get_user_by_telegram_id(telegram_id)
        
        if not user:
            await update.message.reply_text(
                "❌ Error: No se pudo encontrar tu perfil de usuario.\n"
                "Por favor, reinicia el bot con /start"
            )
            return self.bot.ConversationHandler.END
        
        # Agregar user_id
        context.user_data['medicamento']['user_id'] = user['user_id']
        
        try:
            # Guardar en Google Sheets
            medicamento_id = sheets_db.create_medicamento(context.user_data['medicamento'])
            
            # Log de la acción
            sheets_db.log_action(
                user['user_id'],
                'registro_medicamento',
                f'Medicamento registrado: {medicamento_id}',
                result='success'
            )
            
            # Crear resumen
            med = context.user_data['medicamento']
            resumen = (
                f"✅ ¡Medicamento registrado exitosamente!\n\n"
                f"💊 Medicamento: {med['nombre_medicamento']}\n"
                f"💉 Dosis: {med['dosis']}\n"
                f"⏰ Frecuencia: {med['frecuencia']}\n"
                f"📅 Duración: {med['duracion']}\n"
                f"📅 Inicio: {med['fecha_inicio']}\n"
                f"📅 Fin: {med['fecha_fin']}\n"
            )
            
            if med.get('indicaciones'):
                resumen += f"📝 Indicaciones: {med['indicaciones']}\n"
            
            resumen += f"\n🆔 ID de registro: {medicamento_id}"
            
            await update.message.reply_text(
                resumen,
                reply_markup=self.bot.get_main_keyboard()
            )
            
            # Limpiar datos temporales
            context.user_data.pop('medicamento', None)
            return self.bot.MENU_PRINCIPAL
            
        except Exception as e:
            logger.error(f"Error guardando medicamento: {e}")
            await update.message.reply_text(
                "❌ Hubo un error al guardar el medicamento.\n"
                "Por favor, intenta nuevamente más tarde.",
                reply_markup=self.bot.get_main_keyboard()
            )
            return self.bot.MENU_PRINCIPAL
    
    # === FLUJOS DE EXÁMENES ===
    
    async def iniciar_registro_examen(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Inicia el flujo de registro de examen"""
        context.user_data['examen'] = {}
        
        # Ofrecer tipos de examen
        keyboard = [
            ['🩸 Examen de Sangre', '🫀 Electrocardiograma'],
            ['📸 Radiografía', '🧠 Resonancia Magnética'],
            ['🔍 Ecografía', '👁️ Examen Oftalmológico'],
            ['🦴 Densitometría', '📊 Otro tipo de examen'],
            ['🏠 Menú Principal']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "🔬 Registro de Examen Médico\n\n"
            "Te ayudaré a registrar un examen médico.\n\n"
            "¿Qué tipo de examen es?",
            reply_markup=reply_markup
        )
        return self.bot.EXAMEN_TIPO
    
    async def examen_tipo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa el tipo de examen"""
        text = update.message.text.strip()
        
        if text == '🏠 Menú Principal':
            return await self.bot.menu_principal(update, context)
        
        tipos_map = {
            '🩸 Examen de Sangre': 'Examen de Sangre',
            '🫀 Electrocardiograma': 'Electrocardiograma',
            '📸 Radiografía': 'Radiografía',
            '🧠 Resonancia Magnética': 'Resonancia Magnética',
            '🔍 Ecografía': 'Ecografía',
            '👁️ Examen Oftalmológico': 'Examen Oftalmológico',
            '🦴 Densitometría': 'Densitometría'
        }
        
        if text == '📊 Otro tipo de examen':
            await update.message.reply_text(
                "Por favor, escribe el tipo de examen:\n"
                "(Por ejemplo: Colonoscopía, Mamografía, Endoscopía)"
            )
            return self.bot.EXAMEN_TIPO
        
        tipo_examen = tipos_map.get(text, text)
        context.user_data['examen']['tipo_examen'] = tipo_examen
        
        await update.message.reply_text(
            f"Perfecto! 🔬\n\n"
            f"¿Cuál es el nombre específico del examen?\n"
            f"(Por ejemplo: Hemograma completo, Radiografía de tórax, Ecografía abdominal)",
            reply_markup=self.bot.get_cancel_keyboard()
        )
        return self.bot.EXAMEN_NOMBRE
    
    async def examen_nombre(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa el nombre del examen"""
        text = update.message.text.strip()
        
        if text in ['🏠 Menú Principal', '❌ Cancelar']:
            return await self.bot.menu_principal(update, context)
        
        context.user_data['examen']['nombre_examen'] = text
        
        await update.message.reply_text(
            f"Excelente! 📅\n\n"
            f"¿Cuándo fue solicitado este examen? (DD/MM/AAAA)\n"
            f"Si fue hoy, puedes escribir 'hoy'"
        )
        return self.bot.EXAMEN_FECHA_SOLICITUD
    
    async def examen_fecha_solicitud(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa la fecha de solicitud del examen"""
        text = update.message.text.strip()
        
        if text in ['🏠 Menú Principal', '❌ Cancelar']:
            return await self.bot.menu_principal(update, context)
        
        try:
            if text.lower() == 'hoy':
                fecha_solicitud = datetime.now().strftime('%Y-%m-%d')
            else:
                fecha_obj = datetime.strptime(text, '%d/%m/%Y')
                fecha_solicitud = fecha_obj.strftime('%Y-%m-%d')
            
            context.user_data['examen']['fecha_solicitud'] = fecha_solicitud
            
            # Preguntar si ya fue realizado
            keyboard = [
                ['✅ Sí, ya lo hice', '⏳ No, está pendiente'],
                ['🏠 Menú Principal']
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                f"Perfecto! 🔬\n\n"
                f"¿Ya te realizaste este examen?",
                reply_markup=reply_markup
            )
            return self.bot.EXAMEN_FECHA_REALIZACION
            
        except ValueError:
            await update.message.reply_text(
                "❌ Formato de fecha incorrecto.\n\n"
                "Por favor usa el formato DD/MM/AAAA o escribe 'hoy'"
            )
            return self.bot.EXAMEN_FECHA_SOLICITUD
    
    async def examen_fecha_realizacion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa si el examen fue realizado"""
        text = update.message.text.strip()
        
        if text == '🏠 Menú Principal':
            return await self.bot.menu_principal(update, context)
        
        if text == '⏳ No, está pendiente':
            context.user_data['examen']['fecha_realizacion'] = ''
            context.user_data['examen']['resultado'] = ''
            context.user_data['examen']['observaciones'] = ''
            context.user_data['examen']['archivo_url'] = ''
            
            # Guardar examen pendiente
            return await self.guardar_examen(update, context, pendiente=True)
        
        elif text == '✅ Sí, ya lo hice':
            await update.message.reply_text(
                f"Genial! 📅\n\n"
                f"¿En qué fecha te lo realizaste? (DD/MM/AAAA)\n"
                f"Si fue hoy, puedes escribir 'hoy'"
            )
            context.user_data['examen_realizado'] = True
            return self.bot.EXAMEN_FECHA_REALIZACION
        
        else:
            # Es una fecha
            try:
                if text.lower() == 'hoy':
                    fecha_realizacion = datetime.now().strftime('%Y-%m-%d')
                else:
                    fecha_obj = datetime.strptime(text, '%d/%m/%Y')
                    fecha_realizacion = fecha_obj.strftime('%Y-%m-%d')
                
                context.user_data['examen']['fecha_realizacion'] = fecha_realizacion
                
                await update.message.reply_text(
                    f"Perfecto! 📋\n\n"
                    f"¿Cuál fue el resultado del examen?\n"
                    f"(Puedes describir los resultados principales o escribir 'normal' si todo salió bien)"
                )
                return self.bot.EXAMEN_RESULTADO
                
            except ValueError:
                await update.message.reply_text(
                    "❌ Formato de fecha incorrecto.\n\n"
                    "Por favor usa el formato DD/MM/AAAA o escribe 'hoy'"
                )
                return self.bot.EXAMEN_FECHA_REALIZACION
    
    async def examen_resultado(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa el resultado del examen"""
        text = update.message.text.strip()
        
        if text in ['🏠 Menú Principal', '❌ Cancelar']:
            return await self.bot.menu_principal(update, context)
        
        context.user_data['examen']['resultado'] = text
        
        await update.message.reply_text(
            f"Excelente! 📝\n\n"
            f"¿Hay alguna observación adicional sobre el examen?\n"
            f"(Opcional - puedes escribir 'no' para omitir)"
        )
        return self.bot.EXAMEN_OBSERVACIONES
    
    async def examen_observaciones(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa las observaciones del examen y lo guarda"""
        text = update.message.text.strip()
        
        if text in ['🏠 Menú Principal', '❌ Cancelar']:
            return await self.bot.menu_principal(update, context)
        
        context.user_data['examen']['observaciones'] = text if text.lower() != 'no' else ''
        context.user_data['examen']['archivo_url'] = ''  # Por ahora sin archivos
        
        return await self.guardar_examen(update, context, pendiente=False)
    
    async def guardar_examen(self, update: Update, context: ContextTypes.DEFAULT_TYPE, pendiente=False):
        """Guarda el examen en la base de datos"""
        telegram_id = str(update.effective_user.id)
        user = sheets_db.get_user_by_telegram_id(telegram_id)
        
        if not user:
            await update.message.reply_text(
                "❌ Error: No se pudo encontrar tu perfil de usuario.\n"
                "Por favor, reinicia el bot con /start"
            )
            return self.bot.ConversationHandler.END
        
        # Agregar user_id
        context.user_data['examen']['user_id'] = user['user_id']
        
        try:
            # Guardar en Google Sheets
            examen_id = sheets_db.create_examen(context.user_data['examen'])
            
            # Log de la acción
            sheets_db.log_action(
                user['user_id'],
                'registro_examen',
                f'Examen registrado: {examen_id}',
                result='success'
            )
            
            # Crear resumen
            examen = context.user_data['examen']
            
            if pendiente:
                resumen = (
                    f"✅ ¡Examen registrado como pendiente!\n\n"
                    f"🔬 Tipo: {examen['tipo_examen']}\n"
                    f"📋 Nombre: {examen['nombre_examen']}\n"
                    f"📅 Fecha solicitado: {examen['fecha_solicitud']}\n"
                    f"⏳ Estado: Pendiente de realización\n\n"
                    f"💡 Consejo: Puedes actualizar este registro cuando tengas los resultados.\n\n"
                    f"🆔 ID de registro: {examen_id}"
                )
            else:
                resumen = (
                    f"✅ ¡Examen registrado exitosamente!\n\n"
                    f"🔬 Tipo: {examen['tipo_examen']}\n"
                    f"📋 Nombre: {examen['nombre_examen']}\n"
                    f"📅 Fecha solicitado: {examen['fecha_solicitud']}\n"
                    f"📅 Fecha realizado: {examen['fecha_realizacion']}\n"
                    f"📊 Resultado: {examen['resultado']}\n"
                )
                
                if examen.get('observaciones'):
                    resumen += f"📝 Observaciones: {examen['observaciones']}\n"
                
                resumen += f"\n🆔 ID de registro: {examen_id}"
            
            await update.message.reply_text(
                resumen,
                reply_markup=self.bot.get_main_keyboard()
            )
            
            # Limpiar datos temporales
            context.user_data.pop('examen', None)
            return self.bot.MENU_PRINCIPAL
            
        except Exception as e:
            logger.error(f"Error guardando examen: {e}")
            await update.message.reply_text(
                "❌ Hubo un error al guardar el examen.\n"
                "Por favor, intenta nuevamente más tarde.",
                reply_markup=self.bot.get_main_keyboard()
            )
            return self.bot.MENU_PRINCIPAL
    
    # === GESTIÓN DE FAMILIARES ===
    
    async def gestionar_familiares(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Menú de gestión de familiares"""
        telegram_id = str(update.effective_user.id)
        user = sheets_db.get_user_by_telegram_id(telegram_id)
        
        if not user:
            await update.message.reply_text(
                "❌ Error: No se pudo encontrar tu perfil de usuario."
            )
            return self.bot.MENU_PRINCIPAL
        
        # Obtener familiares autorizados
        familiares = sheets_db.get_familiares_autorizados(user['user_id'])
        
        mensaje = f"👨‍👩‍👧‍👦 Gestión de Familiares\n\n"
        
        if familiares:
            mensaje += f"Familiares autorizados ({len(familiares)}):\n\n"
            for familiar in familiares:
                nombre = familiar.get('nombre_familiar', 'Sin nombre')
                parentesco = familiar.get('parentesco', 'Sin parentesco')
                permisos = familiar.get('permisos', 'lectura')
                mensaje += f"• {nombre} ({parentesco}) - {permisos}\n"
            mensaje += "\n"
        else:
            mensaje += "No tienes familiares autorizados aún.\n\n"
        
        keyboard = [
            ['➕ Agregar Familiar', '📋 Ver Familiares'],
            ['🔒 Gestionar Permisos', '🏠 Menú Principal']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(mensaje, reply_markup=reply_markup)
        return self.bot.MENU_PRINCIPAL
    
    async def configuracion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Menú de configuración del usuario"""
        telegram_id = str(update.effective_user.id)
        user = sheets_db.get_user_by_telegram_id(telegram_id)
        
        if not user:
            await update.message.reply_text(
                "❌ Error: No se pudo encontrar tu perfil de usuario."
            )
            return self.bot.MENU_PRINCIPAL
        
        nombre = user.get('nombre', 'Sin nombre')
        email = user.get('email', 'No registrado')
        telefono = user.get('telefono', 'No registrado')
        plan = user.get('plan', 'freemium')
        
        mensaje = (
            f"⚙️ Configuración de tu cuenta\n\n"
            f"👤 Nombre: {nombre}\n"
            f"📧 Email: {email}\n"
            f"📱 Teléfono: {telefono}\n"
            f"💎 Plan: {plan.title()}\n\n"
            f"¿Qué te gustaría hacer?"
        )
        
        keyboard = [
            ['✏️ Actualizar Datos', '🔒 Cambiar Permisos'],
            ['💎 Mejorar Plan', '📊 Exportar Datos'],
            ['🗑️ Eliminar Cuenta', '🏠 Menú Principal']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(mensaje, reply_markup=reply_markup)
        return self.bot.MENU_PRINCIPAL 