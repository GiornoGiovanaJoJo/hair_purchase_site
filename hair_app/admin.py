"""
Django Admin configuration for hair purchase application
with custom dashboard and beautiful UI
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from .models import HairApplication, PriceList, TelegramAdmin
from .admin_views import get_dashboard_stats, get_chart_data, get_recent_applications
from . import admin_views_export


class CustomAdminSite(admin.AdminSite):
    """Custom admin site with dashboard"""
    site_header = "Hair Purchase Admin Panel"
    site_title = "Администрация"
    index_title = "Добро пожаловать в панель управления"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export/applications/csv/', admin_views_export.export_applications_csv, name='export-applications-csv'),
            path('export/applications/excel/', admin_views_export.export_applications_excel, name='export-applications-excel'),
            path('export/prices/excel/', admin_views_export.export_prices_excel, name='export-prices-excel'),
        ]
        return custom_urls + urls
    
    def index(self, request):
        """Custom dashboard page"""
        from django.shortcuts import render
        
        stats = get_dashboard_stats()
        chart_data = get_chart_data()
        recent_apps = get_recent_applications(10)
        
        context = {
            'stats': stats,
            'chart_data': chart_data,
            'recent_apps': recent_apps,
            'site_header': self.site_header,
            'title': 'Dashboard',
        }
        return render(request, 'admin/custom_dashboard.html', context)


# Create and register custom admin site
try:
    custom_admin_site = CustomAdminSite(name='custom_admin')
except Exception as e:
    print(f'Warning: Failed to create custom admin site: {e}')
    custom_admin_site = admin.site


class HairApplicationAdmin(admin.ModelAdmin):
    """Admin for hair applications with beautiful styling."""
    
    list_display = [
        'application_badge',
        'customer_info',
        'status_badge',
        'hair_specs',
        'price_badge',
        'created_date',
    ]
    
    list_filter = ['status', 'length', 'color', 'structure', 'condition', 'created_at']
    search_fields = ['name', 'phone', 'email', 'city', 'comment', 'id']
    readonly_fields = ['estimated_price', 'created_at', 'updated_at', 'display_photos']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'phone', 'email', 'city', 'comment')
        }),
        ('Характеристики волос', {
            'fields': ('length', 'color', 'structure', 'age', 'condition')
        }),
        ('Фотографии', {
            'fields': ('photo1', 'photo2', 'photo3', 'display_photos')
        }),
        ('Цена и статус', {
            'fields': ('estimated_price', 'final_price', 'status', 'admin_notes')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_accepted', 'mark_as_rejected', 'mark_as_completed']
    ordering = ('-created_at',)
    
    def application_badge(self, obj):
        return format_html(
            '<span style="background-color: #0f3460; color: white; padding: 6px 12px; border-radius: 12px; font-weight: bold; font-size: 12px;">ID #{}</span>',
            obj.id
        )
    application_badge.short_description = 'Заявка'
    
    def customer_info(self, obj):
        phone_link = f'<a href="tel:{obj.phone}">{obj.phone}</a>' if obj.phone else '---'
        email_link = f'<a href="mailto:{obj.email}">{obj.email}</a>' if obj.email else '---'
        city = f' ({obj.city})' if obj.city else ''
        return format_html(
            '<div style="line-height: 1.6; font-size: 12px;"><strong>{}</strong>{}<br/>Phone: {}<br/>Email: {}</div>',
            obj.name or '---', city, phone_link, email_link
        )
    customer_info.short_description = 'Клиент'
    
    def status_badge(self, obj):
        status_map = {
            'new': ('Новая', '#f39c12'),
            'viewed': ('Просмотрена', '#3498db'),
            'accepted': ('Принята', '#27ae60'),
            'rejected': ('Отклонена', '#e74c3c'),
            'completed': ('Завершена', '#16a085'),
        }
        display, color = status_map.get(obj.status, ('---', '#95a5a6'))
        return format_html(
            '<span style="background-color: {}; color: white; padding: 6px 12px; border-radius: 12px; font-weight: bold; font-size: 12px;">{}</span>',
            color, display
        )
    status_badge.short_description = 'Статус'
    
    def hair_specs(self, obj):
        return format_html(
            '<div style="line-height: 1.6; font-size: 11px;">{} см<br/>{} / {}<br/>{} / {}</div>',
            obj.length if obj.length else '---',
            obj.color if obj.color else '---',
            obj.condition if obj.condition else '---',
            obj.structure if obj.structure else '---',
            obj.age if obj.age else '---'
        )
    hair_specs.short_description = 'Волосы'
    
    def price_badge(self, obj):
        if obj.final_price:
            price_text = str(int(obj.final_price))
            return format_html(
                '<span style="background-color: #27ae60; color: white; padding: 6px 12px; border-radius: 8px; font-weight: bold; font-size: 12px;">RUB {}</span>',
                price_text
            )
        elif obj.estimated_price:
            price_text = str(int(obj.estimated_price))
            return format_html(
                '<span style="background-color: #3498db; color: white; padding: 6px 12px; border-radius: 8px; font-weight: bold; font-size: 12px;">~RUB {}</span>',
                price_text
            )
        return '---'
    price_badge.short_description = 'Цена'
    
    def created_date(self, obj):
        return format_html(
            '<span title="{}" style="color: #7f8c8d; font-size: 12px;">{}</span>',
            obj.created_at.strftime('%d.%m.%Y %H:%M:%S'),
            obj.created_at.strftime('%d.%m')
        )
    created_date.short_description = 'Дата'
    
    def display_photos(self, obj):
        html = '<div style="display: flex; gap: 10px; flex-wrap: wrap;">'
        for photo in [obj.photo1, obj.photo2, obj.photo3]:
            if photo:
                html += f'<img src="{photo.url}" style="max-width: 200px; max-height: 200px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'
        html += '</div>'
        return format_html(html)
    display_photos.short_description = 'Фотографии'
    
    def mark_as_accepted(self, request, queryset):
        updated = queryset.filter(status='new').update(status='accepted')
        self.message_user(request, f'{updated} заявок принято')
    mark_as_accepted.short_description = 'Принять выбранные'
    
    def mark_as_rejected(self, request, queryset):
        updated = queryset.filter(status='new').update(status='rejected')
        self.message_user(request, f'{updated} заявок отклонено')
    mark_as_rejected.short_description = 'Отклонить выбранные'
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.filter(status__in=['accepted']).update(status='completed')
        self.message_user(request, f'{updated} заявок завершено')
    mark_as_completed.short_description = 'Завершить выбранные'


class PriceListAdmin(admin.ModelAdmin):
    """Admin for price list with beautiful display."""
    
    list_display = ['price_id', 'color_badge', 'length_display', 'structure_display', 'condition_display', 'price_display', 'active_badge']
    list_filter = ['length', 'color', 'structure', 'condition', 'is_active']
    search_fields = ['length', 'color', 'structure']
    
    fieldsets = (
        ('Параметры', {
            'fields': ('length', 'color', 'structure', 'condition')
        }),
        ('Цена', {
            'fields': ('base_price', 'is_active')
        }),
    )
    
    def price_id(self, obj):
        return format_html(
            '<span style="background-color: #e94560; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">#{}</span>',
            obj.id
        )
    price_id.short_description = 'ID'
    
    def color_badge(self, obj):
        color_map = {
            'блонд': ('Блонд', '#FFD700'),
            'светло-русые': ('Светло-русые', '#F5DEB3'),
            'русые': ('Русые', '#8D6E63'),
            'темно-русые': ('Тёмно-русые', '#704214'),
            'каштановые': ('Каштановые', '#3E2723'),
        }
        display, bg_color = color_map.get(obj.color, (obj.color, '#95a5a6'))
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">{}</span>',
            bg_color, display
        )
    color_badge.short_description = 'Цвет'
    
    def length_display(self, obj):
        return f'{obj.length}'
    length_display.short_description = 'Длина'
    
    def structure_display(self, obj):
        return f'{obj.structure}'
    structure_display.short_description = 'Структура'
    
    def condition_display(self, obj):
        return f'{obj.condition}'
    condition_display.short_description = 'Состояние'
    
    def price_display(self, obj):
        price_text = str(int(obj.base_price))
        return format_html(
            '<span style="background-color: #27ae60; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;">RUB {}</span>',
            price_text
        )
    price_display.short_description = 'Цена'
    
    def active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #27ae60; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">АКТИВНА</span>'
            )
        return format_html(
            '<span style="background-color: #95a5a6; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">НЕАКТИВНА</span>'
        )
    active_badge.short_description = 'Статус'


class TelegramAdminAdmin(admin.ModelAdmin):
    """Admin for Telegram administrators."""
    
    list_display = ['user_badge', 'username_link', 'active_status', 'permissions_display']
    list_filter = ['is_active', 'can_manage_applications', 'can_manage_prices']
    search_fields = ['telegram_id', 'username', 'first_name', 'last_name']
    
    fieldsets = (
        ('Информация', {
            'fields': ('telegram_id', 'username', 'first_name', 'last_name')
        }),
        ('Роли и права', {
            'fields': ('is_active', 'can_manage_applications', 'can_manage_prices')
        }),
    )
    
    readonly_fields = ['telegram_id']
    
    def user_badge(self, obj):
        return format_html(
            '<span style="background-color: #00BCD4; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">ID: {}</span>',
            obj.telegram_id
        )
    user_badge.short_description = 'Telegram ID'
    
    def username_link(self, obj):
        if obj.username:
            return format_html(
                '<a href="https://t.me/{}" target="_blank" style="text-decoration: none; color: #0f3460; font-weight: bold;">@{}</a> ({})',
                obj.username, obj.username, obj.first_name or '---'
            )
        return obj.first_name or '---'
    username_link.short_description = 'Пользователь'
    
    def active_status(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #27ae60; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">АКТИВЕН</span>'
            )
        return format_html(
            '<span style="background-color: #95a5a6; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">НЕАКТИВЕН</span>'
        )
    active_status.short_description = 'Статус'
    
    def permissions_display(self, obj):
        perms = []
        if obj.can_manage_applications:
            perms.append('Заявки')
        if obj.can_manage_prices:
            perms.append('Цены')
        return ' | '.join(perms) if perms else '---'
    permissions_display.short_description = 'Права'


# Register with custom admin site if available, otherwise use default
try:
    custom_admin_site.register(HairApplication, HairApplicationAdmin)
    custom_admin_site.register(PriceList, PriceListAdmin)
    custom_admin_site.register(TelegramAdmin, TelegramAdminAdmin)
except Exception as e:
    print(f'Warning: Failed to register with custom admin: {e}')
    admin.site.register(HairApplication, HairApplicationAdmin)
    admin.site.register(PriceList, PriceListAdmin)
    admin.site.register(TelegramAdmin, TelegramAdminAdmin)
