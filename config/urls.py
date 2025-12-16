"""
URL Configuration for hair purchase site project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)
from hair_app import admin_views_export
from hair_app.admin import custom_admin_site

urlpatterns = [
    # Admin Export URLs
    path('admin/export/applications/csv/', admin_views_export.export_applications_csv, name='export-applications-csv'),
    path('admin/export/applications/excel/', admin_views_export.export_applications_excel, name='export-applications-excel'),
    path('admin/export/prices/excel/', admin_views_export.export_prices_excel, name='export-prices-excel'),
    
    # Custom Admin with Dashboard
    path('admin/', custom_admin_site.urls),
    
    # Main app
    path('', include('hair_app.urls')),
    
    # API Documentation (OpenAPI/Swagger)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
