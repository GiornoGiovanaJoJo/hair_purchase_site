"""
Views for hair purchase application
"""
import logging
from decimal import Decimal
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

logger = logging.getLogger(__name__)


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
        try:
            # Log incoming data for debugging
            logger.info(f"Creating hair application with data: {self.request.data}")
            
            # Calculate estimated price
            estimated_price = calculate_hair_price(
                length=serializer.validated_data['length'],
                color=serializer.validated_data['color'],
                structure=serializer.validated_data['structure'],
                age=serializer.validated_data['age'],  # ДОБАВЛЕНО
                condition=serializer.validated_data['condition']
            )
            
            logger.info(f"Calculated estimated price: {estimated_price}")
            
            # Save application
            application = serializer.save(estimated_price=estimated_price)
            
            logger.info(f"Application created successfully with ID: {application.id}")
            
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
                logger.info(f"Email notification sent for application #{application.id}")
            except Exception as e:
                # Log error but don't fail the request
                logger.error(f'Error sending email for application #{application.id}: {e}')
                
        except Exception as e:
            logger.error(f'Error creating hair application: {e}', exc_info=True)
            raise


@extend_schema(
    request=PriceCalculatorSerializer,
    responses={200: {'type': 'object', 'properties': {
        'estimated_price': {'type': 'number'},
        'min_price': {'type': 'number'},
        'max_price': {'type': 'number'}
    }}},
    description='Рассчитать предварительную стоимость волос'
)
@api_view(['POST'])
def calculate_price(request):
    """
    Calculate estimated price with range.
    """
    try:
        logger.info(f"Calculating price with data: {request.data}")
        
        serializer = PriceCalculatorSerializer(data=request.data)
        
        if serializer.is_valid():
            estimated_price = calculate_hair_price(
                length=serializer.validated_data['length'],
                color=serializer.validated_data['color'],
                structure=serializer.validated_data['structure'],
                age=serializer.validated_data['age'],  # ДОБАВЛЕНО
                condition=serializer.validated_data['condition']
            )
            
            # Рассчитываем диапазон ±20% - ДОБАВЛЕНО
            min_price = (estimated_price * Decimal('0.8')).quantize(Decimal('0.01'))
            max_price = (estimated_price * Decimal('1.2')).quantize(Decimal('0.01'))
            
            logger.info(f"Calculated price: {estimated_price}, range: {min_price}-{max_price}")
            
            return Response({
                'estimated_price': float(estimated_price),
                'min_price': float(min_price),  # ДОБАВЛЕНО
                'max_price': float(max_price)   # ДОБАВЛЕНО
            })
        
        logger.warning(f"Price calculation validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f'Error calculating price: {e}', exc_info=True)
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    responses={200: PriceListSerializer(many=True)},
    description='Получить прайс-лист'
)
@api_view(['GET'])
def price_list(request):
    """
    Get active price list.
    """
    try:
        prices = PriceList.objects.filter(is_active=True)
        serializer = PriceListSerializer(prices, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f'Error getting price list: {e}', exc_info=True)
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
