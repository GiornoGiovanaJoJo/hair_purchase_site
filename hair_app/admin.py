"""
Django Admin configuration for hair purchase application
with beautiful UI, colored badges, and improved UX
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from .models import HairApplication, PriceList, TelegramAdmin


@admin.register(HairApplication)
class HairApplicationAdmin(admin.ModelAdmin):
    """Admin for hair applications with beautiful badges and styling."""
    
    list_display = [
        'application_badge',
        'customer_info',
        'status_badge',
        'hair_specs',
        'price_badge',
        'created_date',
    ]
    
    list_filter = [
        'status', 'length', 'color', 'structure', 'condition', 'age', 'created_at'
    ]
    
    search_fields = ['name', 'phone', 'email', 'city', 'comment', 'id']
    
    readonly_fields = ['estimated_price', 'created_at', 'updated_at', 'display_photos']
    
    fieldsets = (
        ('🎯 Основная информация', {
            'fields': ('name', 'phone', 'email', 'city', 'comment')
        }),
        ('🎨 Характеристики волос', {
            'fields': ('length', 'color', 'structure', 'age', 'condition')
        }),
        ('📸 Фотографии', {
            'fields': ('photo1', 'photo2', 'photo3', 'display_photos')
        }),
        ('💰 Стоимость и статус', {
            'fields': ('estimated_price', 'final_price', 'status', 'admin_notes')
        }),
        ('📝 Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_approved', 'mark_as_declined', 'mark_as_completed']
    
    ordering = ('-created_at',)
    
    def application_badge(self, obj):
        """Show application ID with beautiful badge."""
        return format_html(
            '<span style="'
            'background-color: #2196F3; '
            'color: white; '
            'padding: 6px 12px; '
            'border-radius: 12px; '
            'font-weight: bold; '
            'font-size: 12px;'
            '">📋 #{}</span>',
            obj.id
        )
    application_badge.short_description = '🎯 Заявка'
    
    def customer_info(self, obj):
        """Show customer information."""
        phone_link = f'<a href="tel:{obj.phone}">{obj.phone}</a>' if obj.phone else '—'
        email_link = f'<a href="mailto:{obj.email}">{obj.email}</a>' if obj.email else '—'
        city = f' ({obj.city})' if obj.city else ''
        
        return format_html(
            '<div style="line-height: 1.6; font-size: 12px;">'
            '<strong>{}</strong>{}<br/>'
            '📞 {}<br/>'
            '✉️ {}'
            '</div>',
            obj.name or '—',
            city,
            phone_link,
            email_link
        )
    customer_info.short_description = '👤 Клиент'
    
    def status_badge(self, obj):
        """Show status with colored badge."""
        status_map = {
            'new': ('🟡 Новая', '#FFC107'),
            'approved': ('✅ Одобрено', '#4CAF50'),
            'declined': ('❌ Отклонено', '#F44336'),
            'completed': ('🏁 Завершено', '#8BC34A'),
        }
        
        display, color = status_map.get(obj.status, ('—', '#9E9E9E'))
        
        return format_html(
            '<span style="'
            'background-color: {}; '
            'color: white; '
            'padding: 6px 12px; '
            'border-radius: 12px; '
            'font-weight: bold; '
            'font-size: 12px;'
            '">{}}</span>',
            color,
            display
        )
    status_badge.short_description = '⚡ Статус'
    
    def hair_specs(self, obj):
        """Show hair specifications compactly."""
        length_map = {
            '40-60': '40-60',
            '60-80': '60-80',
            '80-100': '80-100',
            '100': '100+',
        }
        
        color_map = {
            'blond': '👱 Блонд',
            'dark': '🟤 Тёмные',
            'brown': '☕ Каштановые',
            'red': '🔴 Рыжие',
        }
        
        condition_map = {
            'natural': '✨ Натуральные',
            'dyed': '🎨 Окрашенные',
            'damaged': '⚠️ Повреждённые',
        }
        
        structure_map = {
            'slavic': '🪡 Славянка',
            'asian': '🪡 Азиатские',
            'mixed': '🪡 Смешанные',
        }
        
        length = length_map.get(str(obj.length), str(obj.length))
        color = color_map.get(obj.color, obj.color)
        condition = condition_map.get(obj.condition, obj.condition)
        structure = structure_map.get(obj.structure, obj.structure)
        
        return format_html(
            '<div style="line-height: 1.6; font-size: 11px;">'
            '{} см<br/>'
            '{} · {}<br/>'
            '{} · {}'
            '</div>',
            length,
            color,
            condition,
            structure,
            f'👧 {obj.get_age_display()}' if hasattr(obj, 'get_age_display') else f'👧 {obj.age}'
        )
    hair_specs.short_description = '💇 Волосы'
    
    def price_badge(self, obj):
        """Show price with styling."""
        if obj.final_price:
            return format_html(
                '<span style="'
                'background-color: #4CAF50; '
                'color: white; '
                'padding: 6px 12px; '
                'border-radius: 8px; '
                'font-weight: bold; '
                'font-size: 12px;'
                '">₽ {:,.0f}</span>',
                obj.final_price
            )
        elif obj.estimated_price:
            return format_html(
                '<span style="'
                'background-color: #2196F3; '
                'color: white; '
                'padding: 6px 12px; '
                'border-radius: 8px; '
                'font-weight: bold; '
                'font-size: 12px;'
                '">~₽ {:,.0f}</span>',
                obj.estimated_price
            )
        return '—'
    price_badge.short_description = '💰 Цена'
    
    def created_date(self, obj):
        """Show creation date."""
        return format_html(
            '<span title="{}" style="color: #666; font-size: 12px;">{}</span>',
            obj.created_at.strftime('%d.%m.%Y %H:%M:%S'),
            obj.created_at.strftime('%d.%m')
        )
    created_date.short_description = '📅 Дата'
    
    def display_photos(self, obj):
        """Display photos in admin."""
        html = '<div style="display: flex; gap: 10px; flex-wrap: wrap;">'
        
        for photo in [obj.photo1, obj.photo2, obj.photo3]:
            if photo:
                html += f'<img src="{photo.url}" style="max-width: 200px; max-height: 200px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'
        
        html += '</div>'
        return format_html(html)
    
    display_photos.short_description = '📸 Превью фото'
    
    def mark_as_approved(self, request, queryset):
        """Action: approve applications."""
        updated = queryset.filter(status='new').update(status='approved')
        self.message_user(request, f'✅ {updated} заявок одобрено')
    mark_as_approved.short_description = '✅ Одобрить выбранные'
    
    def mark_as_declined(self, request, queryset):
        """Action: decline applications."""
        updated = queryset.filter(status='new').update(status='declined')
        self.message_user(request, f'❌ {updated} заявок отклонено')
    mark_as_declined.short_description = '❌ Отклонить выбранные'
    
    def mark_as_completed(self, request, queryset):
        """Action: mark applications as completed."""
        updated = queryset.filter(status__in=['approved']).update(status='completed')
        self.message_user(request, f'🏁 {updated} заявок завершено')
    mark_as_completed.short_description = '🏁 Завершить выбранные'


@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    """Admin for price list with beautiful display."""
    
    list_display = [
        'price_id',
        'color_badge',
        'length_display',
        'structure_display',
        'condition_display',
        'age_badge',
        'price_display',
        'active_badge',
    ]
    
    list_filter = ['length', 'color', 'structure', 'condition', 'age', 'is_active']
    
    search_fields = ['length', 'color', 'structure']
    
    list_editable = ['base_price', 'is_active']
    
    fieldsets = (
        ('📋 Параметры', {
            'fields': ('length', 'color', 'structure', 'condition', 'age')
        }),
        ('💰 Цена', {
            'fields': ('base_price', 'is_active')
        }),
        ('📝 Метаданные', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['updated_at']
    
    def price_id(self, obj):
        return format_html(
            '<span style="'
            'background-color: #E91E63; '
            'color: white; '
            'padding: 4px 8px; '
            'border-radius: 4px; '
            'font-size: 11px; '
            'font-weight: bold;'
            '">#{}</span>',
            obj.id
        )
    price_id.short_description = '🎯 ID'
    
    def color_badge(self, obj):
        color_map = {
            'blond': ('👱 Блонд', '#FFD700'),
            'dark': ('🟤 Тёмные', '#3E2723'),
            'brown': ('☕ Каштановые', '#8D6E63'),
            'red': ('🔴 Рыжие', '#D32F2F'),
        }
        display, bg_color = color_map.get(obj.color, (obj.color, '#9E9E9E'))
        
        return format_html(
            '<span style="'
            'background-color: {}; '
            'color: white; '
            'padding: 4px 8px; '
            'border-radius: 4px; '
            'font-size: 11px; '
            'font-weight: bold;'
            '">{}}</span>',
            bg_color,
            display
        )
    color_badge.short_description = '🎨 Цвет'
    
    def length_display(self, obj):
        return f'📏 {obj.length}+ см'
    length_display.short_description = '📏 Длина'
    
    def structure_display(self, obj):
        structure_map = {
            'slavic': '🪡 Славянка',
            'asian': '🪡 Азиатские',
            'mixed': '🪡 Смешанные',
        }
        return structure_map.get(obj.structure, obj.structure)
    structure_display.short_description = '🪡 Структура'
    
    def condition_display(self, obj):
        condition_map = {
            'natural': '✨ Натуральные',
            'dyed': '🎨 Окрашенные',
            'damaged': '⚠️ Повреждённые',
        }
        return condition_map.get(obj.condition, obj.condition)
    condition_display.short_description = '✨ Состояние'
    
    def age_badge(self, obj):
        age_map = {
            'children': ('👧 Детские', '#FF69B4'),
            'adult': ('👩 Взрослые', '#2196F3'),
        }
        display, bg_color = age_map.get(obj.age, (obj.age, '#9E9E9E'))
        
        return format_html(
            '<span style="'
            'background-color: {}; '
            'color: white; '
            'padding: 4px 8px; '
            'border-radius: 4px; '
            'font-size: 11px; '
            'font-weight: bold;'
            '">{}}</span>',
            bg_color,
            display
        )
    age_badge.short_description = '👥 Возраст'
    
    def price_display(self, obj):
        return format_html(
            '<span style="'
            'background-color: #4CAF50; '
            'color: white; '
            'padding: 4px 8px; '
            'border-radius: 4px; '
            'font-weight: bold; '
            'font-size: 12px;'
            '">₽ {:,.0f}</span>',
            obj.base_price
        )
    price_display.short_description = '💰 Цена'
    
    def active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="'
                'background-color: #4CAF50; '
                'color: white; '
                'padding: 4px 8px; '
                'border-radius: 4px; '
                'font-weight: bold; '
                'font-size: 11px;'
                '">✅ Активна</span>'
            )
        return format_html(
            '<span style="'
            'background-color: #9E9E9E; '
            'color: white; '
            'padding: 4px 8px; '
            'border-radius: 4px; '
            'font-weight: bold; '
            'font-size: 11px;'
            '">⭕ Отключена</span>'
        )
    active_badge.short_description = '⚡ Статус'


@admin.register(TelegramAdmin)
class TelegramAdminAdmin(admin.ModelAdmin):
    """Admin for Telegram administrators."""
    
    list_display = [
        'user_badge',
        'username_link',
        'active_status',
        'permissions_display',
        'created_date',
    ]
    
    list_filter = ['is_active', 'can_manage_applications', 'can_manage_prices', 'created_at']
    
    search_fields = ['telegram_id', 'username', 'first_name', 'last_name']
    
    list_editable = ['is_active']
    
    fieldsets = (
        ('👤 Информация', {
            'fields': ('telegram_id', 'username', 'first_name', 'last_name')
        }),
        ('⚙️ Роли и права', {
            'fields': ('is_active', 'can_manage_applications', 'can_manage_prices')
        }),
        ('📝 Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['telegram_id', 'created_at', 'updated_at']
    
    def user_badge(self, obj):
        return format_html(
            '<span style="'
            'background-color: #00BCD4; '
            'color: white; '
            'padding: 4px 8px; '
            'border-radius: 4px; '
            'font-weight: bold; '
            'font-size: 11px;'
            '">ID: {}</span>',
            obj.telegram_id
        )
    user_badge.short_description = '🆔 Telegram ID'
    
    def username_link(self, obj):
        if obj.username:
            return format_html(
                '<a href="https://t.me/{}" target="_blank" style="text-decoration: none; color: #00BCD4; font-weight: bold;">'
                '@{}</a> ({})',
                obj.username,
                obj.username,
                obj.first_name or '—'
            )
        return obj.first_name or '—'
    username_link.short_description = '👤 Пользователь'
    
    def active_status(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="'
                'background-color: #4CAF50; '
                'color: white; '
                'padding: 4px 8px; '
                'border-radius: 4px; '
                'font-weight: bold; '
                'font-size: 11px;'
                '">🟢 Активен</span>'
            )
        return format_html(
            '<span style="'
            'background-color: #9E9E9E; '
            'color: white; '
            'padding: 4px 8px; '
            'border-radius: 4px; '
            'font-weight: bold; '
            'font-size: 11px;'
            '">⚫ Неактивен</span>'
        )
    active_status.short_description = '⚡ Статус'
    
    def permissions_display(self, obj):
        perms = []
        if obj.can_manage_applications:
            perms.append('📋 Заявки')
        if obj.can_manage_prices:
            perms.append('💰 Цены')
        
        if perms:
            return ' | '.join(perms)
        return '—'
    permissions_display.short_description = '🔐 Права'
    
    def created_date(self, obj):
        return format_html(
            '<span title="{}" style="color: #666; font-size: 12px;">{}</span>',
            obj.created_at.strftime('%d.%m.%Y %H:%M:%S'),
            obj.created_at.strftime('%d.%m')
        )
    created_date.short_description = '📅 Дата'
