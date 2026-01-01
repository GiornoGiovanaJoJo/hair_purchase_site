"""
Асинхронные задачи, запускаемые в отдельных потоках
"""
import logging
from threading import Thread
import asyncio
import time
import sys

logger = logging.getLogger(__name__)


def send_telegram_notification_async(app_id, retry_count=0, max_retries=3):
    """Запустить async функцию Telegram уведомления с ретрайтом"""
    try:
        # Пытаемся импортировать telegram_bot
        try:
            from telegram_bot.bot import send_new_application_notification
        except ImportError as e:
            logger.error(f'[TELEGRAM] Failed to import telegram bot: {e}')
            logger.error('[TELEGRAM] Make sure telegram_bot/bot.py exists and is properly configured')
            return
        
        # Новый event loop для этого потока
        if sys.platform == 'win32':
            # Windows требует ProactorEventLoop
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            logger.info(f'[TELEGRAM] Sending notification for app #{app_id} (attempt {retry_count + 1}/{max_retries + 1})')
            loop.run_until_complete(send_new_application_notification(app_id))
            logger.info(f'[TELEGRAM] ✅ Notification sent successfully for app #{app_id}')
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f'[TELEGRAM] ❌ Notification failed for app #{app_id}: {e}', exc_info=True)
        
        # Пытаемся повторить
        if retry_count < max_retries:
            logger.warning(f'[TELEGRAM] Retrying in 3 seconds... (attempt {retry_count + 2}/{max_retries + 1})')
            time.sleep(3)
            send_telegram_notification_async(app_id, retry_count + 1, max_retries)
        else:
            logger.error(f'[TELEGRAM] ❌ Max retries exceeded for app #{app_id}')


def send_telegram_notification(app_id):
    """
    Запустить Telegram уведомление в отдельном потоке (non-blocking)
    Ото решает проблему доставки постанутгов погорению соединения
    
    Args:
        app_id: ID заявки для отправки уведомления
    """
    thread = Thread(
        target=send_telegram_notification_async,
        args=(app_id,),
        daemon=False,  # Не daemon - чтобы отдать сквазь
        name=f'telegram-notifier-{app_id}'
    )
    thread.start()
    logger.info(f'[TELEGRAM] Notification thread started for app #{app_id}')
