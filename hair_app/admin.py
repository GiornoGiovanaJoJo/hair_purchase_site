"""
Django Admin configuration for hair purchase application
with beautiful UI, colored badges, and improved UX
"""
from django.contrib import admin
from django.utils.html import format_html
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
        'status', 'length', 'color', 'structure', 'condition', 'created_at'
    ]
    
    search_fields = ['name', 'phone', 'email', 'city', 'comment', 'id']
    
    readonly_fields = ['estimated_price', 'created_at', 'updated_at', 'display_photos']
    
    fieldsets = (
        ('Main Information', {
            'fields': ('name', 'phone', 'email', 'city', 'comment')
        }),
        ('Hair Characteristics', {
            'fields': ('length', 'color', 'structure', 'age', 'condition')
        }),
        ('Photos', {
            'fields': ('photo1', 'photo2', 'photo3', 'display_photos')
        }),
        ('Price and Status', {
            'fields': ('estimated_price', 'final_price', 'status', 'admin_notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_accepted', 'mark_as_rejected', 'mark_as_completed']
    
    ordering = ('-created_at',)
    
    def application_badge(self, obj):
        """Show application ID with beautiful badge."""
        return format_html(
            '<span style="background-color: #2196F3; color: white; '
            'padding: 6px 12px; border-radius: 12px; font-weight: bold; '
            'font-size: 12px;">ID #{}</span>',
            obj.id
        )
    application_badge.short_description = 'Application'
    
    def customer_info(self, obj):
        """Show customer information."""
        phone_link = f'<a href="tel:{obj.phone}">{obj.phone}</a>' if obj.phone else '---'
        email_link = f'<a href="mailto:{obj.email}">{obj.email}</a>' if obj.email else '---'
        city = f' ({obj.city})' if obj.city else ''
        
        return format_html(
            '<div style="line-height: 1.6; font-size: 12px;">'
            '<strong>{}</strong>{}<br/>'
            'Phone: {}<br/>'
            'Email: {}</div>',
            obj.name or '---',
            city,
            phone_link,
            email_link
        )
    customer_info.short_description = 'Customer'
    
    def status_badge(self, obj):
        """Show status with colored badge."""
        status_map = {
            'new': ('New', '#FFC107'),
            'viewed': ('Viewed', '#2196F3'),
            'accepted': ('Accepted', '#4CAF50'),
            'rejected': ('Rejected', '#F44336'),
            'completed': ('Completed', '#8BC34A'),
        }
        
        display, color = status_map.get(obj.status, ('---', '#9E9E9E'))
        
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 6px 12px; border-radius: 12px; font-weight: bold; '
            'font-size: 12px;">{}</span>',
            color,
            display
        )
    status_badge.short_description = 'Status'
    
    def hair_specs(self, obj):
        """Show hair specifications compactly."""
        return format_html(
            '<div style="line-height: 1.6; font-size: 11px;">'
            '{} cm<br/>'
            '{} / {}<br/>'
            '{} / {}</div>',
            obj.length if obj.length else '---',
            obj.color if obj.color else '---',
            obj.condition if obj.condition else '---',
            obj.structure if obj.structure else '---',
            obj.age if obj.age else '---'
        )
    hair_specs.short_description = 'Hair Specs'
    
    def price_badge(self, obj):
        """Show price with styling."""
        if obj.final_price:
            return format_html(
                '<span style="background-color: #4CAF50; color: white; '
                'padding: 6px 12px; border-radius: 8px; font-weight: bold; '
                'font-size: 12px;">RUB {:,.0f}</span>',
                obj.final_price
            )
        elif obj.estimated_price:
            return format_html(
                '<span style="background-color: #2196F3; color: white; '
                'padding: 6px 12px; border-radius: 8px; font-weight: bold; '
                'font-size: 12px;">~RUB {:,.0f}</span>',
                obj.estimated_price
            )
        return '---'
    price_badge.short_description = 'Price'
    
    def created_date(self, obj):
        """Show creation date."""
        return format_html(
            '<span title="{}" style="color: #666; font-size: 12px;">{}</span>',
            obj.created_at.strftime('%d.%m.%Y %H:%M:%S'),
            obj.created_at.strftime('%d.%m')
        )
    created_date.short_description = 'Date'
    
    def display_photos(self, obj):
        """Display photos in admin."""
        html = '<div style="display: flex; gap: 10px; flex-wrap: wrap;">'
        
        for photo in [obj.photo1, obj.photo2, obj.photo3]:
            if photo:
                html += f'<img src="{photo.url}" style="max-width: 200px; max-height: 200px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'
        
        html += '</div>'
        return format_html(html)
    
    display_photos.short_description = 'Photos'
    
    def mark_as_accepted(self, request, queryset):
        """Action: accept applications."""
        updated = queryset.filter(status='new').update(status='accepted')
        self.message_user(request, f'{updated} applications accepted')
    mark_as_accepted.short_description = 'Accept Selected'
    
    def mark_as_rejected(self, request, queryset):
        """Action: reject applications."""
        updated = queryset.filter(status='new').update(status='rejected')
        self.message_user(request, f'{updated} applications rejected')
    mark_as_rejected.short_description = 'Reject Selected'
    
    def mark_as_completed(self, request, queryset):
        """Action: mark applications as completed."""
        updated = queryset.filter(status__in=['accepted']).update(status='completed')
        self.message_user(request, f'{updated} applications completed')
    mark_as_completed.short_description = 'Complete Selected'


@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    """Admin for price list with beautiful display."""
    
    list_display = [
        'price_id',
        'color_badge',
        'length_display',
        'structure_display',
        'condition_display',
        'price_display',
        'active_badge',
    ]
    
    list_filter = ['length', 'color', 'structure', 'condition', 'is_active']
    
    search_fields = ['length', 'color', 'structure']
    
    fieldsets = (
        ('Parameters', {
            'fields': ('length', 'color', 'structure', 'condition')
        }),
        ('Price', {
            'fields': ('base_price', 'is_active')
        }),
    )
    
    def price_id(self, obj):
        return format_html(
            '<span style="background-color: #E91E63; color: white; '
            'padding: 4px 8px; border-radius: 4px; font-size: 11px; '
            'font-weight: bold;">#{}</span>',
            obj.id
        )
    price_id.short_description = 'ID'
    
    def color_badge(self, obj):
        color_map = {
            'блонд': ('Blonde', '#FFD700'),
            'светло-русые': ('Light Brown', '#F5DEB3'),
            'русые': ('Brown', '#8D6E63'),
            'темно-русые': ('Dark Brown', '#704214'),
            'каштановые': ('Dark', '#3E2723'),
        }
        display, bg_color = color_map.get(obj.color, (obj.color, '#9E9E9E'))
        
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 4px 8px; border-radius: 4px; font-size: 11px; '
            'font-weight: bold;">{}</span>',
            bg_color,
            display
        )
    color_badge.short_description = 'Color'
    
    def length_display(self, obj):
        return f'{obj.length}'
    length_display.short_description = 'Length'
    
    def structure_display(self, obj):
        return f'{obj.structure}'
    structure_display.short_description = 'Structure'
    
    def condition_display(self, obj):
        return f'{obj.condition}'
    condition_display.short_description = 'Condition'
    
    def price_display(self, obj):
        return format_html(
            '<span style="background-color: #4CAF50; color: white; '
            'padding: 4px 8px; border-radius: 4px; font-weight: bold; '
            'font-size: 12px;">RUB {:,.0f}</span>',
            obj.base_price
        )
    price_display.short_description = 'Price'
    
    def active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #4CAF50; color: white; '
                'padding: 4px 8px; border-radius: 4px; font-weight: bold; '
                'font-size: 11px;">ACTIVE</span>'
            )
        return format_html(
            '<span style="background-color: #9E9E9E; color: white; '
            'padding: 4px 8px; border-radius: 4px; font-weight: bold; '
            'font-size: 11px;">INACTIVE</span>'
        )
    active_badge.short_description = 'Status'


@admin.register(TelegramAdmin)
class TelegramAdminAdmin(admin.ModelAdmin):
    """Admin for Telegram administrators."""
    
    list_display = [
        'user_badge',
        'username_link',
        'active_status',
        'permissions_display',
    ]
    
    list_filter = ['is_active', 'can_manage_applications', 'can_manage_prices']
    
    search_fields = ['telegram_id', 'username', 'first_name', 'last_name']
    
    fieldsets = (
        ('Information', {
            'fields': ('telegram_id', 'username', 'first_name', 'last_name')
        }),
        ('Roles and Permissions', {
            'fields': ('is_active', 'can_manage_applications', 'can_manage_prices')
        }),
    )
    
    readonly_fields = ['telegram_id']
    
    def user_badge(self, obj):
        return format_html(
            '<span style="background-color: #00BCD4; color: white; '
            'padding: 4px 8px; border-radius: 4px; font-weight: bold; '
            'font-size: 11px;">ID: {}</span>',
            obj.telegram_id
        )
    user_badge.short_description = 'Telegram ID'
    
    def username_link(self, obj):
        if obj.username:
            return format_html(
                '<a href="https://t.me/{}" target="_blank" style="text-decoration: none; color: #00BCD4; font-weight: bold;">'
                '@{}</a> ({})',
                obj.username,
                obj.username,
                obj.first_name or '---'
            )
        return obj.first_name or '---'
    username_link.short_description = 'User'
    
    def active_status(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #4CAF50; color: white; '
                'padding: 4px 8px; border-radius: 4px; font-weight: bold; '
                'font-size: 11px;">ACTIVE</span>'
            )
        return format_html(
            '<span style="background-color: #9E9E9E; color: white; '
            'padding: 4px 8px; border-radius: 4px; font-weight: bold; '
            'font-size: 11px;">INACTIVE</span>'
        )
    active_status.short_description = 'Status'
    
    def permissions_display(self, obj):
        perms = []
        if obj.can_manage_applications:
            perms.append('Applications')
        if obj.can_manage_prices:
            perms.append('Prices')
        
        if perms:
            return ' | '.join(perms)
        return '---'
    permissions_display.short_description = 'Permissions'
