"""
Асинхронные задачи, запускаемые в отдельных потоках
"""
import logging
from threading import Thread
import asyncio

logger = logging.getLogger(__name__)


def send_telegram_notification_async(app_id):
    """Запустить async функцию Telegram уведомления"""
    try:
        from telegram_bot.bot import send_new_application_notification
        asyncio.run(send_new_application_notification(app_id))
    except Exception as e:
        logger.error(f'Telegram notification failed for app #{app_id}: {e}')


def send_telegram_notification(app_id):
    """
    Запустить Telegram уведомление в отдельном потоке (non-blocking)
    Это решает проблему "Event loop is closed" в Gunicorn
    
    Args:
        app_id: ID заявки для отправки уведомления
    """
    thread = Thread(
        target=send_telegram_notification_async,
        args=(app_id,),
        daemon=True,
        name=f'telegram-notifier-{app_id}'
    )
    thread.start()
    logger.info(f'Telegram notification thread started for app #{app_id}')
