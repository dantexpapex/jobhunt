import telegram
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)
from config import Config
import logging

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self):
        self.bot = None
        self.chat_id = Config.TELEGRAM_CHAT_ID
        if Config.TELEGRAM_BOT_TOKEN:
            try:
                self.bot = telegram.Bot(token=Config.TELEGRAM_BOT_TOKEN)
            except Exception as e:
                logger.error(f"Error initializing Telegram bot: {e}")

    def send_message(self, text):
        if not self.bot or not self.chat_id:
            logger.warning("Telegram bot not configured")
            return False

        try:
            self.bot.send_message(chat_id=self.chat_id, text=text)
            return True
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

    def send_job_found(self, job_data):
        text = f"🔍 *Nueva oferta encontrada*\n\n"
        text += f"*{job_data.get('title', '')}*\n"
        text += f"🏢 {job_data.get('company', '')}\n"
        text += f"📍 {job_data.get('location', '')}\n"
        text += f"[Ver oferta]({job_data.get('url', '')})"
        return self.send_message(text)

    def send_application_sent(self, job_title, company):
        text = f"✅ *Solicitud enviada*\n\n{job_title} at {company}"
        return self.send_message(text)

    def send_interview_notice(self, job_title, company):
        text = f"🎉 *Entrevista programada*\n\n{job_title} at {company}"
        return self.send_message(text)

    def send_error(self, error_msg):
        text = f"⚠️ *Error*\n\n{error_msg}"
        return self.send_message(text)


async def start_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "🤖 *JobHunt AI*\n\n"
        "Comandos disponibles:\n"
        "/start - Bienvenida\n"
        "/stats - Estadísticas\n"
        "/jobs - Ofertas recientes\n"
        "/apply - Forzar aplicación\n"
        "/stop - Pausar búsqueda\n"
        "/resume - Reanudar búsqueda",
        parse_mode="Markdown",
    )


async def stats_command(update: Update, context: CallbackContext):
    from core.tracker import JobTracker

    tracker = JobTracker()
    stats = tracker.get_stats()

    text = f"📊 *Estadísticas*\n\n"
    text += f"Total ofertas: {stats.get('total_jobs', 0)}\n"
    text += f"Total aplicaciones: {stats.get('total_applications', 0)}\n"
    text += f"Nuevas: {stats.get('status_counts', {}).get('new', 0)}\n"
    text += f"Aplicadas: {stats.get('status_counts', {}).get('applied', 0)}\n"
    text += f"Entrevistas: {stats.get('status_counts', {}).get('interview', 0)}\n"
    text += f"Rechazadas: {stats.get('status_counts', {}).get('rejected', 0)}"

    await update.message.reply_text(text, parse_mode="Markdown")


async def jobs_command(update: Update, context: CallbackContext):
    from core.tracker import JobTracker

    tracker = JobTracker()
    jobs = tracker.get_recent_jobs(10)

    if not jobs:
        await update.message.reply_text("No hay ofertas recientes")
        return

    text = "📋 *Ofertas Recientes*\n\n"
    for job in jobs:
        text += f"• {job.title} @ {job.company}\n"
        text += f"  Score: {job.score or 'N/A'} | [{job.status}]\n\n"

    await update.message.reply_text(text, parse_mode="Markdown")


async def apply_command(update: Update, context: CallbackContext):
    from core.scheduler import trigger_applications

    await update.message.reply_text("🚀 Ejecutando aplicaciones...")
    trigger_applications()
    await update.message.reply_text("✅ Proceso de aplicaciones iniciado")


async def stop_command(update: Update, context: CallbackContext):
    from core.scheduler import stop_scheduler

    stop_scheduler()
    await update.message.reply_text("⏹️ Búsqueda pausada")


async def resume_command(update: Update, context: CallbackContext):
    from core.scheduler import start_scheduler

    start_scheduler()
    await update.message.reply_text("▶️ Búsqueda reiniciada")


def setup_bot():
    if not Config.TELEGRAM_BOT_TOKEN:
        logger.warning("Telegram bot token not configured")
        return None

    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("jobs", jobs_command))
    application.add_handler(CommandHandler("apply", apply_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("resume", resume_command))

    return application


notifier = TelegramNotifier()
