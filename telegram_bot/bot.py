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

# Добавляем корневую директорию проекта в sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Настраиваем Django окружение
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from django.conf import settings
from hair_app.models import HairApplication

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('TELEGRAM_ADMIN_CHAT_ID')

if not TOKEN:
    logger.error("Ошибка: TELEGRAM_BOT_TOKEN не найден в .env")
    sys.exit(1)

if not ADMIN_CHAT_ID:
    logger.error("Ошибка: TELEGRAM_ADMIN_CHAT_ID не найден в .env")
    sys.exit(1)

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
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
    new_apps = HairApplication.objects.filter(status='new').order_by('-created_at')[:5]
    
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
    all_apps = HairApplication.objects.all().order_by('-created_at')[:10]
    
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
    total = HairApplication.objects.count()
    new = HairApplication.objects.filter(status='new').count()
    in_progress = HairApplication.objects.filter(status='in_progress').count()
    completed = HairApplication.objects.filter(status='completed').count()
    rejected = HairApplication.objects.filter(status='rejected').count()
    
    text = (
        "📊 <b>Статистика заявок:</b>\n\n"
        f"📝 Всего: <b>{total}</b>\n"
        f"🆕 Новых: <b>{new}</b>\n"
        f"⏳ В работе: <b>{in_progress}</b>\n"
        f"✅ Завершено: <b>{completed}</b>\n"
        f"❌ Отклонено: <b>{rejected}</b>"
    )
    
    await message.answer(text)

# ====================
# CALLBACK ОБРАБОТЧИКИ
# ====================

@dp.callback_query(F.data.startswith("app_"))
async def process_application_callback(callback: types.CallbackQuery):
    """Обработка кнопок управления заявкой"""
    action, app_id = callback.data.split("_", 1)
    
    try:
        app = HairApplication.objects.get(id=app_id)
    except HairApplication.DoesNotExist:
        await callback.answer("❌ Заявка не найдена", show_alert=True)
        return
    
    if action == "app":
        # Показать подробности заявки
        text = format_application_full(app)
        keyboard = get_application_keyboard(app.id, app.status)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    
    elif action == "accept":
        app.status = 'in_progress'
        app.save()
        await callback.answer("✅ Заявка принята в работу")
        
        # Обновляем кнопки
        keyboard = get_application_keyboard(app.id, app.status)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    
    elif action == "complete":
        app.status = 'completed'
        app.save()
        await callback.answer("✅ Заявка завершена")
        
        keyboard = get_application_keyboard(app.id, app.status)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    
    elif action == "reject":
        app.status = 'rejected'
        app.save()
        await callback.answer("❌ Заявка отклонена")
        
        keyboard = get_application_keyboard(app.id, app.status)
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
    try:
        app = HairApplication.objects.get(id=app_id)
        
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
        
    except HairApplication.DoesNotExist:
        logger.error(f"Заявка #{app_id} не найдена")
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления: {e}")

# ====================
# ЗАПУСК БОТА
# ====================

async def main():
    """Главная функция запуска бота"""
    logger.info("🤖 Бот запущен!")
    
    try:
        # Удаляем старые апдейты
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Отправляем сообщение админу о запуске
        try:
            await bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text="🚀 <b>Бот запущен и готов к работе!</b>\n\nОтправь /start для просмотра команд."
            )
        except Exception as e:
            logger.warning(f"Не удалось отправить сообщение админу: {e}")
        
        # Запускаем polling
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен")