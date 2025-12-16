"""
URL'ы для кастомной админки
"""
from django.urls import path
from . import admin_views_export

app_name = 'admin'

urlpatterns = [
    path('export/applications/csv/', admin_views_export.export_applications_csv, name='export-applications-csv'),
    path('export/applications/excel/', admin_views_export.export_applications_excel, name='export-applications-excel'),
    path('export/prices/excel/', admin_views_export.export_prices_excel, name='export-prices-excel'),
]
