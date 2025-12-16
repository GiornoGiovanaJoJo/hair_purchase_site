"""
URL Configuration for hair_app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .admin_views import dashboard_view, chart_data, recent_applications_api

# API Router
router = DefaultRouter()
router.register(r'applications', views.HairApplicationViewSet, basename='application')

app_name = 'hair_app'

urlpatterns = [
    # Main page
    path('', views.index, name='index'),

    # Admin Dashboard API
    path('api/admin/dashboard/', dashboard_view, name='admin_dashboard_api'),
    path('api/admin/chart/', chart_data, name='admin_chart_api'),
    path('api/admin/recent/', recent_applications_api, name='admin_recent_api'),
    
    # API endpoints
    path('api/', include([
        path('', include(router.urls)),
        path('calculator/', views.calculate_price, name='calculator'),
        path('price-list/', views.price_list, name='price-list'),
    ])),
]
