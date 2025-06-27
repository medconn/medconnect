#!/usr/bin/env python3
"""
MedConnect Bot Supervisor
Supervisor robusto para el bot de Telegram con manejo de errores y reconexión automática.
"""

import os
import sys
import time
import signal
import logging
import subprocess
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_supervisor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BotSupervisor:
    def __init__(self):
        self.bot_process = None
        self.running = True
        self.restart_count = 0
        self.max_restarts = 10
        self.restart_delay = 5
        
        # Verificar variables de entorno requeridas
        self.check_environment_variables()
        
        # Configurar manejadores de señales
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def check_environment_variables(self):
        """Verifica que las variables de entorno necesarias estén configuradas"""
        required_vars = [
            'TELEGRAM_BOT_TOKEN',
            'GOOGLE_SHEETS_ID',
            'GOOGLE_CREDENTIALS_FILE'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Variables de entorno faltantes: {missing_vars}")
            logger.error("💡 Configura las variables de entorno antes de ejecutar el bot")
            sys.exit(1)
        
        logger.info("✅ Variables de entorno verificadas")
    
    def signal_handler(self, signum, frame):
        """Maneja las señales de terminación"""
        logger.info(f"📡 Señal recibida: {signum}")
        self.running = False
        self.stop_bot()
        sys.exit(0)
    
    def start_bot(self):
        """Inicia el proceso del bot"""
        try:
            logger.info("🚀 Iniciando bot de MedConnect...")
            
            # Ejecutar el bot principal
            self.bot_process = subprocess.Popen(
                [sys.executable, 'bot.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            logger.info(f"✅ Bot iniciado con PID: {self.bot_process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error iniciando bot: {e}")
            return False
    
    def stop_bot(self):
        """Detiene el proceso del bot"""
        if self.bot_process:
            try:
                logger.info("🛑 Deteniendo bot...")
                self.bot_process.terminate()
                
                # Esperar hasta 10 segundos para terminación normal
                try:
                    self.bot_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    logger.warning("⚠️ Terminación forzada del bot")
                    self.bot_process.kill()
                
                logger.info("✅ Bot detenido")
                self.bot_process = None
                
            except Exception as e:
                logger.error(f"❌ Error deteniendo bot: {e}")
    
    def is_bot_running(self):
        """Verifica si el bot está ejecutándose"""
        if not self.bot_process:
            return False
        
        poll = self.bot_process.poll()
        return poll is None
    
    def monitor_bot(self):
        """Monitorea el bot y lo reinicia si es necesario"""
        while self.running:
            try:
                if not self.is_bot_running():
                    if self.restart_count < self.max_restarts:
                        logger.warning(f"⚠️ Bot no está ejecutándose. Reinicio #{self.restart_count + 1}")
                        
                        if self.start_bot():
                            self.restart_count += 1
                            logger.info(f"✅ Bot reiniciado exitosamente")
                        else:
                            logger.error(f"❌ Fallo al reiniciar bot")
                            time.sleep(self.restart_delay * 2)
                    else:
                        logger.error(f"❌ Máximo número de reinicios alcanzado ({self.max_restarts})")
                        self.running = False
                        break
                
                # Monitorear cada 30 segundos
                time.sleep(30)
                
            except KeyboardInterrupt:
                logger.info("⌨️ Interrupción de teclado recibida")
                self.running = False
                break
            except Exception as e:
                logger.error(f"❌ Error en el monitoreo: {e}")
                time.sleep(self.restart_delay)
    
    def run(self):
        """Ejecuta el supervisor"""
        logger.info("🏥 MedConnect Bot Supervisor iniciado")
        logger.info(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Iniciar el bot por primera vez
            if self.start_bot():
                # Iniciar monitoreo
                self.monitor_bot()
            else:
                logger.error("❌ No se pudo iniciar el bot")
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"❌ Error crítico en supervisor: {e}")
        finally:
            self.stop_bot()
            logger.info("👋 Supervisor terminado")

def main():
    """Función principal"""
    supervisor = BotSupervisor()
    supervisor.run()

if __name__ == "__main__":
    main() 