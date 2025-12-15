"""
Views for hair purchase application
"""
import logging
import asyncio
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
from .price_calculator import PRICE_TABLE

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
                age=serializer.validated_data.get('age', 'взрослые'),
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
            
            # Send Telegram notification
            try:
                from telegram_bot.bot import send_new_application_notification
                asyncio.run(send_new_application_notification(application.id))
                logger.info(f"Telegram notification sent for application #{application.id}")
            except ImportError:
                logger.warning("Telegram bot module not found. Skipping notification.")
            except Exception as e:
                # Log error but don't fail the request
                logger.error(f'Error sending Telegram notification for application #{application.id}: {e}')
                
        except Exception as e:
            logger.error(f'Error creating hair application: {e}', exc_info=True)
            raise


@extend_schema(
    request=PriceCalculatorSerializer,
    responses={200: {'type': 'object', 'properties': {
        'estimated_price': {'type': 'number'},
        'price_min': {'type': 'number'},
        'price_max': {'type': 'number'},
    }}},
    description='Рассчитать точную стоимость волос по таблице'
)
@api_view(['POST'])
def calculate_price(request):
    """
    Calculate exact price from table with min/max range by structure.
    """
    try:
        logger.info(f"Calculating price with data: {request.data}")
        
        serializer = PriceCalculatorSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                length = serializer.validated_data['length']
                color = serializer.validated_data['color']
                structure = serializer.validated_data['structure']
                age = serializer.validated_data.get('age', 'взрослые')
                condition = serializer.validated_data['condition']
                
                # Get exact price for selected structure
                estimated_price = calculate_hair_price(
                    length=length,
                    color=color,
                    structure=structure,
                    age=age,
                    condition=condition
                )
                
                # Determine length_range for table lookup (supports both '100+' string and numeric values)
                length_range = None
                
                # Check if length is already a range string like '100+'
                if isinstance(length, str):
                    length_str = str(length).strip().lower()
                    if length_str == '100+':
                        length_range = '100+'
                    elif '-' in length_str:
                        # Extract first number from range like "50-60"
                        try:
                            length_num = int(length_str.split('-')[0])
                        except (ValueError, AttributeError):
                            length_num = 50
                    else:
                        # Try to parse as number
                        try:
                            length_num = int(length_str)
                        except ValueError:
                            length_num = 50
                else:
                    # Already a number
                    try:
                        length_num = int(length) if length else 50
                    except (ValueError, TypeError):
                        length_num = 50
                
                # Determine range from numeric length if not already determined
                if length_range is None:
                    if length_num < 50:
                        length_range = '40-50'
                    elif length_num < 60:
                        length_range = '50-60'
                    elif length_num < 80:
                        length_range = '60-80'
                    elif length_num < 100:
                        length_range = '80-100'
                    else:
                        length_range = '100+'
                
                # Normalize color for table lookup
                color_map = {
                    'блонд': 'блонд',
                    'светло-русые': 'светло-русые',
                    'светлорусые': 'светло-русые',
                    'русые': 'русые',
                    'темно-русые': 'темно-русые',
                    'темнорусые': 'темно-русые',
                    'каштановые': 'каштановые',
                    'каштан': 'каштановые',
                }
                normalized_color = color_map.get(str(color).strip().lower(), 'блонд')
                
                # Get min and max prices for this length and color
                price_min = None
                price_max = None
                
                try:
                    if length_range in PRICE_TABLE and normalized_color in PRICE_TABLE[length_range]:
                        prices = list(PRICE_TABLE[length_range][normalized_color].values())
                        if prices:
                            price_min = min(prices)
                            price_max = max(prices)
                except (KeyError, ValueError, TypeError) as e:
                    logger.warning(f"Error getting price range from table: {e}")
                
                # Fallback if unable to get range from table
                if price_min is None or price_max is None:
                    price_min = estimated_price
                    price_max = estimated_price
                
                logger.info(f"Calculated prices - Min: {price_min}, Max: {price_max}, Exact: {estimated_price} for range {length_range}")
                
                return Response({
                    'estimated_price': float(estimated_price),
                    'price_min': float(price_min),
                    'price_max': float(price_max),
                })
            except Exception as e:
                logger.error(f'Error in price calculation logic: {e}', exc_info=True)
                return Response(
                    {'error': f'Ошибка при расчете: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        logger.warning(f"Price calculation validation errors: {serializer.errors}")
        return Response(
            {'errors': serializer.errors, 'message': 'Некорректные данные в запросе'},
            status=status.HTTP_400_BAD_REQUEST
        )
        
    except Exception as e:
        logger.error(f'Error calculating price: {e}', exc_info=True)
        return Response(
            {'error': f'Внутренняя ошибка сервера: {str(e)}'},
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
            {'error': 'Внутренняя ошибка сервера'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
