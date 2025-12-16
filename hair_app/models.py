"""
Models for hair purchase application
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from hair_app.price_calculator import calculate_hair_price


def normalize_phone(phone_value):
    """
    Нормализует телефон в формат +7 (999) 123-45-67
    Принимает:
    - +79991234567
    - +7 999 123 4567
    - +7 (999) 123-45-67
    - 79991234567
    - 89991234567
    """
    if not phone_value:
        return phone_value
    
    # Убираем все символы кроме цифр и +
    cleaned = ''.join(c for c in str(phone_value) if c.isdigit() or c == '+')
    
    # Если нет +, добавляем
    if not cleaned.startswith('+'):
        # Если начинается с 8, заменяем на 7
        if cleaned.startswith('8'):
            cleaned = '7' + cleaned[1:]
        # Если не начинается с 7, добавляем +7
        elif not cleaned.startswith('7'):
            cleaned = '7' + cleaned
        # Иначе просто добавляем +
        else:
            cleaned = '+' + cleaned
    
    # Проверяем, что это российский номер и имеет 11 цифр
    digits = ''.join(c for c in cleaned if c.isdigit())
    if not (cleaned.startswith('+7') and len(digits) == 11):
        return phone_value  # Возвращаем оригинальное значение если не валидно
    
    # Форматируем в +7 (999) 123-45-67
    return f"+{digits[0]} ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"


class HairApplication(models.Model):
    """
    Заявка на продажу волос
    """
    
    # Характеристики волос
    # ОНО ИСПРАВЛЕНО и тЕПЕРЬ СОВПАДАЕТ с price_calculator!
    LENGTH_CHOICES = [
        ('40-50', '40-50 см'),
        ('50-60', '50-60 см'),
        ('60-80', '60-80 см'),    # ИСПРАВЛЕНО! (было '60-70')
        ('80-100', '80-100 см'),  # ИСПРАВЛЕНО! (было '70-80', '80-90', '90-100')
        ('100+', 'Более 100 см'),
    ]
    
    COLOR_CHOICES = [
        ('блонд', 'Блонд (светлые)'),
        ('светло-русые', 'Светло-русые'),
        ('русые', 'Русые'),
        ('темно-русые', 'Темно-русые'),
        ('каштановые', 'Темные (каштановые)'),
    ]
    
    STRUCTURE_CHOICES = [
        ('славянка', 'Славянка (тонкие)'),
        ('среднее', 'Средние'),
        ('густые', 'Густые'),
    ]
    
    AGE_CHOICES = [
        ('детские', 'Детские (до 14 лет)'),
        ('взрослые', 'Взрослые (14+ лет)'),
    ]
    
    CONDITION_CHOICES = [
        ('натуральные', 'Натуральные (не окрашенные)'),
        ('окрашенные', 'Окрашенные'),
        ('после химии', 'После химической завивки'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('viewed', 'Просмотрена'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена'),
        ('completed', 'Завершена'),
    ]
    
    # Валидатор телефона - ✅ ИСПРАВЛЕНО: теперь более гибкий
    # Принимает любые форматы российского номера (7-11 цифр)
    phone_validator = RegexValidator(
        regex=r'^\+?7[\s\-\(\)]*9[\d\s\-\(\)]*[\d\s\-\(\)]*$',
        message='Введите корректный российский номер (например: +7 (911) 957-17-12 или +79119571712)',
        code='invalid_phone_format'
    )
    
    # Характеристики волос
    length = models.CharField(
        max_length=10,
        choices=LENGTH_CHOICES,
        verbose_name='Длина волос'
    )
    
    color = models.CharField(
        max_length=20,
        choices=COLOR_CHOICES,
        verbose_name='Цвет волос'
    )
    
    structure = models.CharField(
        max_length=20,
        choices=STRUCTURE_CHOICES,
        verbose_name='Структура волос'
    )
    
    age = models.CharField(
        max_length=20,
        choices=AGE_CHOICES,
        verbose_name='Возраст'
    )
    
    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        verbose_name='Состояние волос'
    )
    
    # Фотографии
    photo1 = models.ImageField(
        upload_to='hair_photos/%Y/%m/%d/',
        verbose_name='Фото 1',
        help_text='Обязательное'
    )
    
    photo2 = models.ImageField(
        upload_to='hair_photos/%Y/%m/%d/',
        verbose_name='Фото 2',
        blank=True,
        null=True
    )
    
    photo3 = models.ImageField(
        upload_to='hair_photos/%Y/%m/%d/',
        verbose_name='Фото 3',
        blank=True,
        null=True
    )
    
    # Контактные данные
    name = models.CharField(
        max_length=100,
        verbose_name='Имя'
    )
    
    phone = models.CharField(
        max_length=20,
        verbose_name='Телефон',
        validators=[phone_validator],
        help_text='Формат: +7 (999) 123-45-67 или +79991234567'
    )
    
    email = models.EmailField(
        verbose_name='Email',
        blank=True
    )
    
    city = models.CharField(
        max_length=100,
        verbose_name='Город',
        blank=True
    )
    
    # Дополнительная информация
    comment = models.TextField(
        verbose_name='Комментарий',
        blank=True,
        help_text='Дополнительная информация от продавца'
    )
    
    # Расчет стоимости
    estimated_price = models.IntegerField(
        default=0,
        verbose_name='Ориентировочная стоимость',
        help_text='Автоматически рассчитывается по калькулятору'
    )
    
    final_price = models.IntegerField(
        verbose_name='Итоговая стоимость',
        blank=True,
        null=True,
        help_text='Устанавливается администратором'
    )
    
    # Статус и метаданные
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )
    
    admin_notes = models.TextField(
        verbose_name='Заметки администратора',
        blank=True
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Заявка на продажу'
        verbose_name_plural = 'Заявки на продажу'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f'Заявка #{self.pk} - {self.name} ({self.get_status_display()})'
    
    def clean(self):
        """
        Очищаем и нормализуем данные перед сохранением.
        """
        # Нормализуем телефон
        self.phone = normalize_phone(self.phone)
    
    def save(self, *args, **kwargs):
        """
        Оверрайд save для автоматического расчета цены.
        Надо нормализовать данные из модели для калькулятора.
        """
        # Вызываем clean() для нормализации
        self.clean()
        
        # Нормализация значений длины - ТЕПЕРЬ ИСПРАВЛЕНО
        length_map = {
            '40-50': 45,
            '50-60': 55,
            '60-80': 65,    # ИСПРАВЛЕНО! (было '60-70', '70-80', '80-90')
            '80-100': 90,   # ИСПРАВЛЕНО! (было '90-100')
        }
        
        # Нормализация цветов
        # Оставляем как есть
        
        # Нормализация структуры
        structure_map = {
            'славянка': 'славянка',
            'среднее': 'среднее',
            'густые': 'густые',
        }
        
        # Нормализация возраста
        age_map = {
            'детские': 'детские',
            'взрослые': 'взрослые',
        }
        
        # Рассчитываем цену только если её нет
        if not self.estimated_price:
            normalized_length = length_map.get(self.length, 50)
            normalized_structure = structure_map.get(self.structure, 'среднее')
            normalized_age = age_map.get(self.age, 'взрослые')
            
            self.estimated_price = calculate_hair_price(
                length=normalized_length,
                color=self.color,
                condition=self.condition,
                structure=normalized_structure,
                age=normalized_age
            )
        
        super().save(*args, **kwargs)


class PriceList(models.Model):
    """
    Прайс-лист на волосы
    """
    length = models.CharField(
        max_length=10,
        choices=HairApplication.LENGTH_CHOICES,
        verbose_name='Длина'
    )
    
    color = models.CharField(
        max_length=20,
        choices=HairApplication.COLOR_CHOICES,
        verbose_name='Цвет'
    )
    
    structure = models.CharField(
        max_length=20,
        choices=HairApplication.STRUCTURE_CHOICES,
        verbose_name='Структура'
    )
    
    condition = models.CharField(
        max_length=20,
        choices=HairApplication.CONDITION_CHOICES,
        verbose_name='Состояние'
    )
    
    base_price = models.IntegerField(
        verbose_name='Базовая цена',
        validators=[MinValueValidator(0)]
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активно'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Позиция прайс-листа'
        verbose_name_plural = 'Прайс-лист'
        unique_together = ['length', 'color', 'structure', 'condition']
    
    def __str__(self):
        return f'{self.get_length_display()} | {self.get_color_display()} | {self.get_structure_display()} - {self.base_price} ₽'


class TelegramAdmin(models.Model):
    """
    Telegram администраторы бота
    """
    telegram_id = models.BigIntegerField(
        unique=True,
        verbose_name='Telegram ID'
    )
    
    username = models.CharField(
        max_length=100,
        verbose_name='Username',
        blank=True
    )
    
    first_name = models.CharField(
        max_length=100,
        verbose_name='Имя',
        blank=True
    )
    
    last_name = models.CharField(
        max_length=100,
        verbose_name='Фамилия',
        blank=True
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    
    can_manage_applications = models.BooleanField(
        default=True,
        verbose_name='Может управлять заявками'
    )
    
    can_manage_prices = models.BooleanField(
        default=False,
        verbose_name='Может управлять ценами'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )
    
    class Meta:
        verbose_name = 'Telegram администратор'
        verbose_name_plural = 'Telegram администраторы'
    
    def __str__(self):
        name = self.username or f'{self.first_name} {self.last_name}'.strip() or str(self.telegram_id)
        return f'{name} ({self.telegram_id})'
