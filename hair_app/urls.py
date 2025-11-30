"""
URL Configuration for hair_app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API Router
router = DefaultRouter()
router.register(r'applications', views.HairApplicationViewSet, basename='application')

app_name = 'hair_app'

urlpatterns = [
    # Main page
    path('', views.index, name='index'),
    
    # API endpoints
    path('api/', include([
        path('', include(router.urls)),
        path('calculator/', views.calculate_price, name='calculator'),
        path('price-list/', views.price_list, name='price-list'),
    ])),
]
