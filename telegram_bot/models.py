from django.db import models


class TelegramUser(models.Model):
    """Модель для хранения подписчиков бота."""
    
    telegram_id = models.BigIntegerField(
        unique=True,
        verbose_name='Telegram ID'
    )
    username = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Username'
    )
    first_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Фамилия'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    is_admin = models.BooleanField(
        default=False,
        verbose_name='Администратор'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата регистрации'
    )
    
    class Meta:
        verbose_name = 'Telegram пользователь'
        verbose_name_plural = 'Telegram пользователи'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name or ''} {self.last_name or ''} (@{self.username or self.telegram_id})"
