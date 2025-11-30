"""
Telegram Bot Settings
"""
from decouple import config

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN', default='')

# Main admin Telegram ID
TELEGRAM_MAIN_ADMIN_ID = config('TELEGRAM_MAIN_ADMIN_ID', default=0, cast=int)

# Webhook settings (for production)
TELEGRAM_USE_WEBHOOK = config('TELEGRAM_USE_WEBHOOK', default=False, cast=bool)
TELEGRAM_WEBHOOK_URL = config('TELEGRAM_WEBHOOK_URL', default='')
TELEGRAM_WEBHOOK_PATH = config('TELEGRAM_WEBHOOK_PATH', default='/telegram/webhook')
