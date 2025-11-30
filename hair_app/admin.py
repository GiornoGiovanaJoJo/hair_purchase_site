"""
Django Admin configuration for hair purchase application
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import HairApplication, PriceList, TelegramAdmin


@admin.register(HairApplication)
class HairApplicationAdmin(admin.ModelAdmin):
    """Admin for hair applications."""
    
    list_display = [
        'id', 'name', 'phone', 'length', 'color', 'structure',
        'estimated_price', 'final_price', 'status', 'created_at'
    ]
    
    list_filter = [
        'status', 'length', 'color', 'structure', 'condition', 'age', 'created_at'
    ]
    
    search_fields = ['name', 'phone', 'email', 'city', 'comment']
    
    readonly_fields = ['estimated_price', 'created_at', 'updated_at', 'display_photos']
    
    fieldsets = (
        ('Характеристики волос', {
            'fields': ('length', 'color', 'structure', 'age', 'condition')
        }),
        ('Фотографии', {
            'fields': ('photo1', 'photo2', 'photo3', 'display_photos')
        }),
        ('Контактные данные', {
            'fields': ('name', 'phone', 'email', 'city')
        }),
        ('Дополнительно', {
            'fields': ('comment', 'admin_notes')
        }),
        ('Стоимость и статус', {
            'fields': ('estimated_price', 'final_price', 'status')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def display_photos(self, obj):
        """Display photos in admin."""
        html = '<div style="display: flex; gap: 10px;">'
        
        if obj.photo1:
            html += f'<img src="{obj.photo1.url}" style="max-width: 200px; max-height: 200px;">'
        
        if obj.photo2:
            html += f'<img src="{obj.photo2.url}" style="max-width: 200px; max-height: 200px;">'
        
        if obj.photo3:
            html += f'<img src="{obj.photo3.url}" style="max-width: 200px; max-height: 200px;">'
        
        html += '</div>'
        return format_html(html)
    
    display_photos.short_description = 'Превью фото'


@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    """Admin for price list."""
    
    list_display = [
        'id', 'length', 'color', 'structure', 'condition',
        'base_price', 'is_active', 'updated_at'
    ]
    
    list_filter = ['length', 'color', 'structure', 'condition', 'is_active']
    
    search_fields = ['length', 'color', 'structure']
    
    list_editable = ['base_price', 'is_active']


@admin.register(TelegramAdmin)
class TelegramAdminAdmin(admin.ModelAdmin):
    """Admin for Telegram administrators."""
    
    list_display = [
        'telegram_id', 'username', 'first_name', 'last_name',
        'is_active', 'can_manage_applications', 'can_manage_prices',
        'created_at'
    ]
    
    list_filter = ['is_active', 'can_manage_applications', 'can_manage_prices']
    
    search_fields = ['telegram_id', 'username', 'first_name', 'last_name']
    
    list_editable = ['is_active', 'can_manage_applications', 'can_manage_prices']
