#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Telegram Bot для управления заявками на скупку волос
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Устанавливаем UTF-8 для Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Добавляем корневую директорию проекта в sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# ЗАГРУЗКА .env ФАЙЛА
try:
    from dotenv import load_dotenv
    env_path = BASE_DIR / '.env'
    load_dotenv(dotenv_path=env_path)
    print(f"[OK] .env загружен из: {env_path}")
except ImportError:
    print("[WARNING] python-dotenv не установлен. Установите: pip install python-dotenv")
    print("Пытаюсь продолжить без .env...")

# Настраиваем Django окружение
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from asgiref.sync import sync_to_async
from django.conf import settings
from hair_app.models import HairApplication

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Инициализация бота
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('TELEGRAM_ADMIN_CHAT_ID')

if not TOKEN:
    logger.error("[ERROR] TELEGRAM_BOT_TOKEN не найден!")
    logger.error("Проверь файл .env и убедись, что переменная установлена:")
    logger.error("TELEGRAM_BOT_TOKEN=твой_токен_от_BotFather")
    sys.exit(1)

if not ADMIN_CHAT_ID:
    logger.error("[ERROR] TELEGRAM_ADMIN_CHAT_ID не найден!")
    logger.error("Проверь файл .env и убедись, что переменная установлена:")
    logger.error("TELEGRAM_ADMIN_CHAT_ID=твой_chat_id")
    sys.exit(1)

logger.info(f"[OK] Токен бота: {TOKEN[:20]}...")
logger.info(f"[OK] Admin Chat ID: {ADMIN_CHAT_ID}")

# Инициализация бота с новым синтаксисом aiogram 3.7.0+
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# ====================
# КОМАНДЫ
# ====================

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Приветственное сообщение"""
    await message.answer(
        "👋 <b>Привет!</b>\n\n"
        "Я бот для управления заявками на скупку волос.\n\n"
        "<b>Доступные команды:</b>\n"
        "/start - Показать это сообщение\n"
        "/new - Посмотреть новые заявки\n"
        "/all - Посмотреть все заявки\n"
        "/stats - Статистика\n\n"
        f"🔑 <b>Your Chat ID:</b> <code>{message.from_user.id}</code>\n"
        "(Скопируй этот ID в TELEGRAM_ADMIN_CHAT_ID в .env)"
    )

@dp.message(Command("new"))
async def cmd_new_applications(message: types.Message):
    """Показать новые заявки"""
    # Используем sync_to_async для Django ORM
    @sync_to_async
    def get_new_apps():
        return list(HairApplication.objects.filter(status='new').order_by('-created_at')[:5])
    
    new_apps = await get_new_apps()
    
    if not new_apps:
        await message.answer("📋 <b>Новых заявок нет</b>")
        return
    
    text = f"🆕 <b>Новые заявки ({len(new_apps)}):</b>\n\n"
    
    for app in new_apps:
        text += format_application_short(app)
        text += "\n" + "-" * 30 + "\n\n"
    
    await message.answer(text)

@dp.message(Command("all"))
async def cmd_all_applications(message: types.Message):
    """Показать все заявки"""
    @sync_to_async
    def get_all_apps():
        return list(HairApplication.objects.all().order_by('-created_at')[:10])
    
    all_apps = await get_all_apps()
    
    if not all_apps:
        await message.answer("📋 <b>Заявок нет</b>")
        return
    
    text = f"📄 <b>Последние {len(all_apps)} заявок:</b>\n\n"
    
    for app in all_apps:
        text += format_application_short(app)
        text += "\n" + "-" * 30 + "\n\n"
    
    await message.answer(text)

@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    """Показать статистику"""
    @sync_to_async
    def get_stats():
        return {
            'total': HairApplication.objects.count(),
            'new': HairApplication.objects.filter(status='new').count(),
            'in_progress': HairApplication.objects.filter(status='in_progress').count(),
            'completed': HairApplication.objects.filter(status='completed').count(),
            'rejected': HairApplication.objects.filter(status='rejected').count(),
        }
    
    stats = await get_stats()
    
    text = (
        "📊 <b>Статистика заявок:</b>\n\n"
        f"📝 Всего: <b>{stats['total']}</b>\n"
        f"🆕 Новых: <b>{stats['new']}</b>\n"
        f"⏳ В работе: <b>{stats['in_progress']}</b>\n"
        f"✅ Завершено: <b>{stats['completed']}</b>\n"
        f"❌ Отклонено: <b>{stats['rejected']}</b>"
    )
    
    await message.answer(text)

# ====================
# CALLBACK ОБРАБОТЧИКИ
# ====================

@dp.callback_query(F.data.startswith("app_"))
async def process_application_callback(callback: types.CallbackQuery):
    """Обработка кнопок управления заявкой"""
    action, app_id = callback.data.split("_", 1)
    
    @sync_to_async
    def get_app(app_id):
        try:
            return HairApplication.objects.get(id=app_id)
        except HairApplication.DoesNotExist:
            return None
    
    @sync_to_async
    def update_app_status(app, status):
        app.status = status
        app.save()
    
    app = await get_app(app_id)
    
    if not app:
        await callback.answer("❌ Заявка не найдена", show_alert=True)
        return
    
    if action == "app":
        # Показать подробности заявки
        text = format_application_full(app)
        keyboard = get_application_keyboard(app.id, app.status)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    elif action == "accept":
        await update_app_status(app, 'in_progress')
        await callback.answer("✅ Заявка принята в работу")
        
        # Обновляем кнопки
        keyboard = get_application_keyboard(app.id, 'in_progress')
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    
    elif action == "complete":
        await update_app_status(app, 'completed')
        await callback.answer("✅ Заявка завершена")
        
        keyboard = get_application_keyboard(app.id, 'completed')
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    
    elif action == "reject":
        await update_app_status(app, 'rejected')
        await callback.answer("❌ Заявка отклонена")
        
        keyboard = get_application_keyboard(app.id, 'rejected')
        await callback.message.edit_reply_markup(reply_markup=keyboard)

# ====================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ====================

def format_application_short(app: HairApplication) -> str:
    """Краткое описание заявки"""
    status_emoji = {
        'new': '🆕',
        'in_progress': '⏳',
        'completed': '✅',
        'rejected': '❌'
    }
    
    emoji = status_emoji.get(app.status, '📝')
    status_text = app.get_status_display()
    
    text = (
        f"{emoji} <b>Заявка #{app.id}</b>\n"
        f"👤 {app.full_name}\n"
        f"📞 {app.phone}\n"
        f"📅 {app.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"🎯 Статус: <b>{status_text}</b>"
    )
    
    return text

def format_application_full(app: HairApplication) -> str:
    """Полное описание заявки"""
    status_text = app.get_status_display()
    
    text = (
        f"📝 <b>Заявка #{app.id}</b>\n\n"
        f"👤 <b>Имя:</b> {app.full_name}\n"
        f"📞 <b>Телефон:</b> {app.phone}\n"
    )
    
    if app.email:
        text += f"📧 <b>Email:</b> {app.email}\n"
    
    if app.city:
        text += f"🏙 <b>Город:</b> {app.city}\n"
    
    if app.hair_length:
        text += f"\n📏 <b>Длина волос:</b> {app.hair_length} см\n"
    
    if app.hair_description:
        text += f"📝 <b>Описание:</b> {app.hair_description}\n"
    
    text += (
        f"\n📅 <b>Дата создания:</b> {app.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"🎯 <b>Статус:</b> {status_text}"
    )
    
    return text

def get_application_keyboard(app_id: int, status: str) -> InlineKeyboardMarkup:
    """Создать клавиатуру для заявки"""
    buttons = []
    
    if status == 'new':
        buttons.append([
            InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{app_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{app_id}")
        ])
    elif status == 'in_progress':
        buttons.append([
            InlineKeyboardButton(text="✅ Завершить", callback_data=f"complete_{app_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{app_id}")
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def send_new_application_notification(app_id: int):
    """
    Отправить уведомление о новой заявке.
    Эту функцию нужно вызвать из Django view после создания заявки.
    """
    @sync_to_async
    def get_app(app_id):
        try:
            return HairApplication.objects.get(id=app_id)
        except HairApplication.DoesNotExist:
            return None
    
    try:
        app = await get_app(app_id)
        
        if not app:
            logger.error(f"Заявка #{app_id} не найдена")
            return
        
        text = (
            "🆕 <b>НОВАЯ ЗАЯВКА!</b>\n\n"
            + format_application_full(app)
        )
        
        keyboard = get_application_keyboard(app.id, app.status)
        
        # Отправляем текстовое уведомление
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=text,
            reply_markup=keyboard
        )
        
        # Отправляем фотографии, если есть
        photo_fields = ['photo1', 'photo2', 'photo3']
        media_group = []
        
        for field_name in photo_fields:
            photo_field = getattr(app, field_name, None)
            if photo_field and photo_field.name:
                try:
                    file_path = photo_field.path
                    if os.path.exists(file_path):
                        media_group.append(
                            types.InputMediaPhoto(
                                media=types.FSInputFile(file_path),
                                caption=f"🖼 Фото {field_name[-1]}" if len(media_group) == 0 else None
                            )
                        )
                except Exception as e:
                    logger.error(f"Ошибка при загрузке фото {field_name}: {e}")
        
        if media_group:
            await bot.send_media_group(
                chat_id=ADMIN_CHAT_ID,
                media=media_group
            )
        
        logger.info(f"Уведомление о заявке #{app_id} отправлено")
        
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления: {e}")

# ====================
# ЗАПУСК БОТА
# ====================

async def main():
    """Главная функция запуска бота"""
    logger.info("[BOT] Бот запущен!")
    
    try:
        # Удаляем старые апдейты
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Отправляем сообщение админу о запуске
        try:
            await bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text="🚀 <b>Бот запущен и готов к работе!</b>\n\nОтправь /start для просмотра команд."
            )
            logger.info("[BOT] Уведомление о запуске отправлено админу")
        except Exception as e:
            logger.warning(f"[BOT] Не удалось отправить сообщение админу: {e}")
        
        # Запускаем polling
        logger.info("[BOT] Запуск polling...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"[BOT] Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("[BOT] Бот остановлен")