#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Утилита для отправки Telegram-уведомлений из Django
"""

import os
import asyncio
import logging
from typing import Optional
from aiogram import Bot
from aiogram.types import FSInputFile, InputMediaPhoto
from aiogram.enums import ParseMode

logger = logging.getLogger(__name__)

# Получаем настройки из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_ADMIN_CHAT_ID = os.getenv('TELEGRAM_ADMIN_CHAT_ID')

def send_application_notification(application_id: int) -> bool:
    """
    Отправить уведомление о новой заявке в Telegram.
    
    Используется в Django view после создания заявки.
    
    Args:
        application_id: ID заявки в базе данных
        
    Returns:
        True если уведомление отправлено, False в противном случае
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_ADMIN_CHAT_ID:
        logger.warning("Не настроены TELEGRAM_BOT_TOKEN или TELEGRAM_ADMIN_CHAT_ID")
        return False
    
    try:
        # Запускаем асинхронную отправку
        asyncio.run(_send_notification(application_id))
        return True
    except Exception as e:
        logger.error(f"Ошибка при отправке Telegram-уведомления: {e}")
        return False

async def _send_notification(application_id: int):
    """Внутренняя асинхронная функция отправки"""
    from hair_app.models import HairApplication
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    bot = Bot(token=TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)
    
    try:
        app = HairApplication.objects.get(id=application_id)
        
        # Формируем текст уведомления
        text = (
            "🆕 <b>НОВАЯ ЗАЯВКА!</b>\n\n"
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
            text += f"📝 <b>Описание:</b>\n{app.hair_description}\n"
        
        text += f"\n📅 <b>Дата:</b> {app.created_at.strftime('%d.%m.%Y %H:%M')}"
        
        # Создаем кнопки управления
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{app.id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{app.id}")
            ]
        ])
        
        # Отправляем текстовое уведомление
        await bot.send_message(
            chat_id=TELEGRAM_ADMIN_CHAT_ID,
            text=text,
            reply_markup=keyboard
        )
        
        # Отправляем фотографии
        media_group = []
        photo_fields = ['photo1', 'photo2', 'photo3']
        
        for i, field_name in enumerate(photo_fields, 1):
            photo_field = getattr(app, field_name, None)
            if photo_field and photo_field.name:
                try:
                    file_path = photo_field.path
                    if os.path.exists(file_path):
                        media_group.append(
                            InputMediaPhoto(
                                media=FSInputFile(file_path),
                                caption=f"🖼 Фото {i} — Заявка #{app.id}" if i == 1 else None
                            )
                        )
                except Exception as e:
                    logger.error(f"Ошибка при загрузке фото {field_name}: {e}")
        
        if media_group:
            await bot.send_media_group(
                chat_id=TELEGRAM_ADMIN_CHAT_ID,
                media=media_group
            )
        
        logger.info(f"✅ Уведомление о заявке #{application_id} отправлено")
        
    except HairApplication.DoesNotExist:
        logger.error(f"Заявка #{application_id} не найдена")
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления: {e}")
        raise
    finally:
        await bot.session.close()