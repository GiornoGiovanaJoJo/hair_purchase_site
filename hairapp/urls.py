from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSet
router = DefaultRouter()
router.register(r'applications', views.HairApplicationViewSet, basename='application')

urlpatterns = [
    # API endpoints from router (auto-generated)
    # GET /api/applications/ - list all
    # POST /api/applications/ - create new
    # GET /api/applications/{id}/ - retrieve one
    # PUT /api/applications/{id}/ - update
    # DELETE /api/applications/{id}/ - delete
    
    # Custom endpoints
    path('calculate-price/', views.calculate_price, name='calculate-price'),
    path('price-list/', views.price_list, name='price-list'),
]

# Add router URLs
urlpatterns += router.urls
