"""
Views for hair purchase application
"""
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import HairApplication, PriceList
from .serializers import (
    HairApplicationSerializer,
    PriceCalculatorSerializer,
    PriceListSerializer
)
from .utils import calculate_hair_price


def index(request):
    """
    Main page view.
    """
    return render(request, 'index.html')


@extend_schema_view(
    list=extend_schema(description='Получить список заявок'),
    create=extend_schema(description='Создать новую заявку'),
    retrieve=extend_schema(description='Получить детали заявки'),
)
class HairApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for hair applications.
    """
    queryset = HairApplication.objects.all()
    serializer_class = HairApplicationSerializer
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        """
        Save application and calculate estimated price.
        """
        # Calculate estimated price
        estimated_price = calculate_hair_price(
            length=serializer.validated_data['length'],
            color=serializer.validated_data['color'],
            structure=serializer.validated_data['structure'],
            condition=serializer.validated_data['condition']
        )
        
        # Save application
        application = serializer.save(estimated_price=estimated_price)
        
        # Send email notification to admin
        try:
            send_mail(
                subject=f'Новая заявка #{application.id}',
                message=f'Получена новая заявка на продажу волос.\n\n'
                        f'Имя: {application.name}\n'
                        f'Телефон: {application.phone}\n'
                        f'Длина: {application.get_length_display()}\n'
                        f'Цвет: {application.get_color_display()}\n'
                        f'Предварительная цена: {application.estimated_price} руб.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=True,
            )
        except Exception as e:
            # Log error but don't fail the request
            print(f'Error sending email: {e}')


@extend_schema(
    request=PriceCalculatorSerializer,
    responses={200: {'type': 'object', 'properties': {'estimated_price': {'type': 'number'}}}},
    description='Рассчитать предварительную стоимость волос'
)
@api_view(['POST'])
def calculate_price(request):
    """
    Calculate hair price based on characteristics.
    """
    serializer = PriceCalculatorSerializer(data=request.data)
    
    if serializer.is_valid():
        estimated_price = calculate_hair_price(
            length=serializer.validated_data['length'],
            color=serializer.validated_data['color'],
            structure=serializer.validated_data['structure'],
            condition=serializer.validated_data['condition']
        )
        
        return Response({
            'estimated_price': estimated_price
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    responses={200: PriceListSerializer(many=True)},
    description='Получить прайс-лист'
)
@api_view(['GET'])
def price_list(request):
    """
    Get active price list.
    """
    prices = PriceList.objects.filter(is_active=True)
    serializer = PriceListSerializer(prices, many=True)
    return Response(serializer.data)
