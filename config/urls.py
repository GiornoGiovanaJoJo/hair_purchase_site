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
from hair_app.admin_views import (
    dashboard,
    get_stats_api,
    get_trend_data_api,
    get_applications_by_status
)

urlpatterns = [
    # Custom Admin Dashboard - MUST be BEFORE admin.site.urls!
    path('admin/dashboard/', dashboard, name='admin_dashboard'),
    path('admin/api/stats/', get_stats_api, name='admin_stats_api'),
    path('admin/api/trend/', get_trend_data_api, name='admin_trend_api'),
    path('admin/api/applications-by-status/', get_applications_by_status, name='admin_status_api'),
    
    # Django Admin - catches all /admin/* paths
    path('admin/', admin.site.urls),
    
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

# Admin site customization
admin.site.site_header = '📋 Admin Panel | Hair Purchase'
admin.site.site_title = 'Administration'
admin.site.index_title = '🏙️ Dashboard Management'
