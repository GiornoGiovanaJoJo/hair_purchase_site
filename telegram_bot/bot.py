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
        "Н бот для управления заявками на скупку волос.\n\n"
        "<b>Доступные команды:</b>\n"
        "/start - Показать это сообщение\n"
        "/queue - Показать все незавершённые заявки (📂 очередь)\n"
        "/all - Показать все заявки\n"
        "/stats - Статистика\n\n"
        f"🔑 <b>Your Chat ID:</b> <code>{message.from_user.id}</code>\n"
        "(Скопируй этот ID в TELEGRAM_ADMIN_CHAT_ID в .env)"
    )

@dp.message(Command("queue"))
async def cmd_queue_applications(message: types.Message):
    """Показать все незавершённые заявки (новые, просмотренные, принятые)"""
    @sync_to_async
    def get_pending_apps():
        # Восюде кроме completed и rejected
        return list(HairApplication.objects.exclude(
            status__in=['completed', 'rejected']
        ).order_by('-created_at'))
    
    pending_apps = await get_pending_apps()
    
    if not pending_apps:
        await message.answer("📂 <b>Очередь пуста</b>")
        return
    
    # Статистика
    new_count = sum(1 for app in pending_apps if app.status == 'new')
    viewed_count = sum(1 for app in pending_apps if app.status == 'viewed')
    accepted_count = sum(1 for app in pending_apps if app.status == 'accepted')
    
    summary = (
        f"📂 <b>Очередь заявок ({len(pending_apps)}):</b>\n\n"
        f"🔵 🎭 Активных:\n"
        f"   🕴 Просмотренных: {viewed_count}\n"
        f"   🟄 Принятых: {accepted_count}\n"
        f"   📥 Новых: {new_count}\n\n"
    )
    
    await message.answer(summary)
    
    # Отправляем каждую заявку отдельным сообщением
    for app in pending_apps:
        text = format_application_full(app)
        keyboard = get_application_keyboard(app.id, app.status)
        await message.answer(text, reply_markup=keyboard)
        await asyncio.sleep(0.1)  # Короткая задержка для Telegram

@dp.message(Command("all"))
async def cmd_all_applications(message: types.Message):
    """Показать все заявки"""
    @sync_to_async
    def get_all_apps():
        return list(HairApplication.objects.all().order_by('-created_at')[:15])
    
    all_apps = await get_all_apps()
    
    if not all_apps:
        await message.answer("📂 <b>Заявок нет</b>")
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
            'viewed': HairApplication.objects.filter(status='viewed').count(),
            'accepted': HairApplication.objects.filter(status='accepted').count(),
            'completed': HairApplication.objects.filter(status='completed').count(),
            'rejected': HairApplication.objects.filter(status='rejected').count(),
        }
    
    stats = await get_stats()
    
    text = (
        "📈 <b>Статистика заявок:</b>\n\n"
        f"📋 Всего: <b>{stats['total']}</b>\n"
        f"📥 Новых: <b>{stats['new']}</b>\n"
        f"🕴 Просмотрено: <b>{stats['viewed']}</b>\n"
        f"✅ Принято: <b>{stats['accepted']}</b>\n"
        f"🎉 Завершено: <b>{stats['completed']}</b>\n"
        f❌ Отклонено: <b>{stats['rejected']}</b>"
    )
    
    await message.answer(text)

# ====================
# CALLBACK ОБРАБОТЧИКИ
# ====================

@dp.callback_query(F.data.regexp(r'^(view|accept|complete|reject)_\d+$'))
async def process_application_callback(callback: types.CallbackQuery):
    """Обработка кнопок управления заявкой"""
    try:
        # Парсим callback_data: "action_app_id"
        parts = callback.data.split('_')
        if len(parts) != 2:
            logger.error(f"Неверный формат callback_data: {callback.data}")
            await callback.answer("❌ Ошибка формата данных", show_alert=True)
            return
        
        action, app_id_str = parts
        app_id = int(app_id_str)
        
        logger.info(f"Обработка callback: action={action}, app_id={app_id}")
        
        @sync_to_async
        def get_app(app_id):
            try:
                return HairApplication.objects.get(id=app_id)
            except HairApplication.DoesNotExist:
                return None
        
        @sync_to_async
        def update_app_status(app, status):
            old_status = app.status
            app.status = status
            app.save()
            logger.info(f"Заявка #{app.id}: статус изменен {old_status} -> {status}")
            return old_status
        
        app = await get_app(app_id)
        
        if not app:
            await callback.answer("❌ Заявка не найдена", show_alert=True)
            return
        
        # Обрабатываем действия
        if action == "view":
            # Просмотр заявки - АВТОМАТИЧЕСКИ меняем статус на "viewed"
            if app.status == 'new':
                await update_app_status(app, 'viewed')
            
            text = format_application_full(app)
            keyboard = get_application_keyboard(app.id, app.status)
            
            await callback.message.edit_text(text, reply_markup=keyboard)
            await callback.answer("🕴 Заявка просмотрена")
        
        elif action == "accept":
            old_status = await update_app_status(app, 'accepted')
            
            # Обновляем текст и кнопки
            text = format_application_full(app)
            keyboard = get_application_keyboard(app.id, 'accepted')
            
            await callback.message.edit_text(text, reply_markup=keyboard)
            await callback.answer("✅ Заявка принята в работу")
        
        elif action == "complete":
            old_status = await update_app_status(app, 'completed')
            
            text = format_application_full(app)
            keyboard = get_application_keyboard(app.id, 'completed')
            
            await callback.message.edit_text(text, reply_markup=keyboard)
            await callback.answer("🎉 Заявка завершена!")
        
        elif action == "reject":
            old_status = await update_app_status(app, 'rejected')
            
            text = format_application_full(app)
            keyboard = get_application_keyboard(app.id, 'rejected')
            
            await callback.message.edit_text(text, reply_markup=keyboard)
            await callback.answer("❌ Заявка отклонена")
    
    except Exception as e:
        logger.error(f"Ошибка в process_application_callback: {e}", exc_info=True)
        await callback.answer("❌ Ошибка обработки", show_alert=True)

# ====================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ====================

def format_application_short(app: HairApplication) -> str:
    """Краткое описание заявки"""
    status_emoji = {
        'new': '📥',
        'viewed': '🕴',
        'accepted': '✅',
        'completed': '🎉',
        'rejected': '❌'
    }
    
    emoji = status_emoji.get(app.status, '📋')
    status_text = app.get_status_display()
    
    text = (
        f"{emoji} <b>Заявка #{app.id}</b>\n"
        f"👤 {app.name}\n"
        f"📂 {app.phone}\n"
        f"📅 {app.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"🎯 Статус: <b>{status_text}</b>"
    )
    
    return text

def format_application_full(app: HairApplication) -> str:
    """Полное описание заявки"""
    status_emoji = {
        'new': '📥',
        'viewed': '🕴',
        'accepted': '✅',
        'completed': '🎉',
        'rejected': '❌'
    }
    
    emoji = status_emoji.get(app.status, '📋')
    status_text = app.get_status_display()
    
    text = (
        f"{emoji} <b>Заявка #{app.id}</b>\n\n"
        f"👤 <b>Имя:</b> {app.name}\n"
        f"📂 <b>Телефон:</b> {app.phone}\n"
    )
    
    if app.email:
        text += f"📧 <b>Email:</b> {app.email}\n"
    
    if app.city:
        text += f"🎫 <b>Город:</b> {app.city}\n"
    
    text += f"\n📐 <b>Длина:</b> {app.get_length_display()}\n"
    text += f"🎫 <b>Цвет:</b> {app.get_color_display()}\n"
    text += f"🔬 <b>Структура:</b> {app.get_structure_display()}\n"
    text += f"👶 <b>Возраст:</b> {app.get_age_display()}\n"
    text += f"👧 <b>Состояние:</b> {app.get_condition_display()}\n"
    
    if app.comment:
        text += f"\n🗣 <b>Комментарий:</b> {app.comment}\n"
    
    if app.estimated_price:
        text += f"\n💰 <b>Предв. цена:</b> {app.estimated_price} ₽\n"
    
    text += (
        f"\n📅 <b>Создано:</b> {app.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"🎯 <b>Статус:</b> {status_text}"
    )
    
    return text

def get_application_keyboard(app_id: int, status: str) -> InlineKeyboardMarkup:
    """Создать клавиатуру для заявки в зависимости от статуса"""
    buttons = []
    
    if status == 'new':
        # Новая заявка: можно просмотреть, принять или отклонить
        buttons.append([
            InlineKeyboardButton(text="🕴 Просмотреть", callback_data=f"view_{app_id}")
        ])
        buttons.append([
            InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{app_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{app_id}")
        ])
    
    elif status == 'viewed':
        # Просмотренная: можно принять или отклонить
        buttons.append([
            InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{app_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{app_id}")
        ])
    
    elif status == 'accepted':
        # Принятая: можно завершить или отклонить
        buttons.append([
            InlineKeyboardButton(text="🎉 Завершить", callback_data=f"complete_{app_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{app_id}")
        ])
    
    elif status == 'completed':
        # Завершенная: кнопок нет
        pass
    
    elif status == 'rejected':
        # Отклоненная: кнопок нет
        pass
    
    return InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else InlineKeyboardMarkup(inline_keyboard=[])

async def send_new_application_notification(app_id: int):
    """
    Отправить уведомление о новой заявке.
    Вызывается из Django view после сохранения заявки.
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
            "🔔 <b>НОВАЙ ЗАЯВКА!</b>\n\n"
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
                    logger.error(f"Ошибка при загруже фото {field_name}: {e}")
        
        if media_group:
            await bot.send_media_group(
                chat_id=ADMIN_CHAT_ID,
                media=media_group
            )
        
        logger.info(f"✅ Уведомление о заявке #{app_id} отправлено успешно")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке уведомления о заявке #{app_id}: {e}", exc_info=True)

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
        logger.info("[BOT] Запуск поллинг...")
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
