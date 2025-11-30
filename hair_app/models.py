"""
Models for hair purchase application
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class HairApplication(models.Model):
    """
    Заявка на продажу волос
    """
    
    # Характеристики волос
    LENGTH_CHOICES = [
        ('40-50', '40-50 см'),
        ('50-60', '50-60 см'),
        ('60-70', '60-70 см'),
        ('70-80', '70-80 см'),
        ('80-90', '80-90 см'),
        ('90-100', '90-100 см'),
        ('100+', 'Более 100 см'),
    ]
    
    COLOR_CHOICES = [
        ('blonde', 'Блонд (светлые)'),
        ('light', 'Светло-русые'),
        ('medium', 'Русые'),
        ('dark', 'Темно-русые'),
        ('brown', 'Темные (каштановые)'),
    ]
    
    STRUCTURE_CHOICES = [
        ('thin', 'Славянка (тонкие)'),
        ('medium', 'Средние'),
        ('thick', 'Густые'),
    ]
    
    AGE_CHOICES = [
        ('child', 'Детские (до 14 лет)'),
        ('adult', 'Взрослые (14+ лет)'),
    ]
    
    CONDITION_CHOICES = [
        ('natural', 'Натуральные (не окрашенные)'),
        ('dyed', 'Окрашенные'),
        ('perm', 'После химической завивки'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('viewed', 'Просмотрена'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена'),
        ('completed', 'Завершена'),
    ]
    
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
        verbose_name='Телефон'
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
    estimated_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Предварительная стоимость',
        help_text='Рассчитанная автоматически'
    )
    
    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
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
    
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
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
        return f'{self.get_length_display()} | {self.get_color_display()} | {self.get_structure_display()} - {self.base_price} руб.'


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
