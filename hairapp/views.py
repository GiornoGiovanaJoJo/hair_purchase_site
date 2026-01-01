import logging
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import HairApplication, PriceList
from .serializers import HairApplicationSerializer, PriceCalculatorSerializer, PriceListSerializer
from .pricecalculator import calculate_hair_price, PRICE_TABLE

logger = logging.getLogger(__name__)


def index(request):
    """Main page view."""
    return render(request, 'index.html')


class HairApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for hair applications."""
    queryset = HairApplication.objects.all()
    serializer_class = HairApplicationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """Create a new hair application.
        
        Returns:
            - 201 Created with application data and estimated_price
            - 400 Bad Request with validation errors
            - 500 Internal Server Error
        """
        try:
            logger.info(f"Creating hair application with data: {request.data}")
            
            # Validate with serializer
            serializer = self.get_serializer(data=request.data)
            
            if not serializer.is_valid():
                logger.warning(f"Validation errors: {serializer.errors}")
                return Response(
                    {
                        'status': 'error',
                        'message': 'Ошибка при заполнении формы. Проверьте все поля.',
                        'errors': serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Perform create and save
            self.perform_create(serializer)
            
            return Response(
                {
                    'status': 'success',
                    'message': 'Заявка успешно создана!',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            logger.error(f"Error creating hair application: {str(e)}", exc_info=True)
            return Response(
                {
                    'status': 'error',
                    'message': f'Внутренняя ошибка сервера: {str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_create(self, serializer):
        """Save application and calculate estimated price."""
        try:
            # Get validated data
            validated_data = serializer.validated_data
            
            # Calculate estimated price
            estimated_price = calculate_hair_price(
                length=validated_data.get('hair_length'),
                color=validated_data.get('hair_color'),
                structure=validated_data.get('hair_structure'),
                age=validated_data.get('hair_age', 0),
                condition=validated_data.get('hair_condition')
            )
            
            logger.info(f"Calculated estimated price: {estimated_price}")
            
            # Save application with estimated price
            application = serializer.save(estimated_price=estimated_price)
            
            # Send email notification
            try:
                send_mail(
                    subject=f'Новая заявка #{application.id}',
                    message=f"""
                    Новая заявка на скупку волос:
                    
                    Имя: {application.name}
                    Телефон: {application.phone}
                    Email: {application.email or 'не указан'}
                    Город: {application.city or 'не указан'}
                    
                    Цвет: {application.hair_color}
                    Длина: {application.hair_length} см
                    Структура: {application.hair_structure}
                    Возраст: {application.hair_age} месяцев
                    Состояние: {application.hair_condition}
                    
                    Комментарий: {application.comment or 'нет'}
                    
                    Примерная стоимость: {estimated_price} руб.
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=settings.ADMIN_EMAIL,
                    fail_silently=True,
                )
                logger.info(f"Email notification sent for application {application.id}")
            except Exception as e:
                logger.error(f"Error sending email for application {application.id}: {str(e)}")
            
            # Send Telegram notification (if configured)
            try:
                from .tasks import send_telegram_notification
                send_telegram_notification(application.id)
                logger.info(f"Telegram notification queued for application {application.id}")
            except ImportError:
                logger.warning("Telegram bot module not found. Skipping notification.")
            except Exception as e:
                logger.error(f"Error queuing Telegram notification for application {application.id}: {str(e)}")
            
            logger.info(f"Application created successfully with ID {application.id}")
        
        except Exception as e:
            logger.error(f"Error in perform_create: {str(e)}", exc_info=True)
            raise


@extend_schema(
    request=PriceCalculatorSerializer,
    responses={200: {'type': 'object', 'properties': {
        'estimated_price': {'type': 'number'},
        'price_min': {'type': 'number'},
        'price_max': {'type': 'number'},
    }}},
    description='Рассчитать примерную стоимость волос'
)
@api_view(['POST'])
def calculate_price(request):
    """Calculate exact price from table with min/max range by structure."""
    try:
        logger.info(f"Calculating price with data: {request.data}")
        
        serializer = PriceCalculatorSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                length = serializer.validated_data['hair_length']
                color = serializer.validated_data['hair_color']
                structure = serializer.validated_data['hair_structure']
                age = serializer.validated_data.get('hair_age', 0)
                condition = serializer.validated_data['hair_condition']
                
                # Calculate exact price
                estimated_price = calculate_hair_price(
                    length=length,
                    color=color,
                    structure=structure,
                    age=age,
                    condition=condition
                )
                
                # Get price range from table if possible
                price_min = None
                price_max = None
                
                try:
                    # Normalize length to range
                    if length < 50:
                        length_range = '40-50'
                    elif length < 60:
                        length_range = '50-60'
                    elif length < 70:
                        length_range = '60-70'
                    elif length < 80:
                        length_range = '70-80'
                    else:
                        length_range = '80-100'
                    
                    # Try to get price range from table
                    if length_range in PRICE_TABLE and color in PRICE_TABLE[length_range]:
                        prices = list(PRICE_TABLE[length_range][color].values())
                        if prices:
                            price_min = min(prices)
                            price_max = max(prices)
                    
                    # Fallback: use estimated price as min/max
                    if price_min is None or price_max is None:
                        price_min = estimated_price
                        price_max = estimated_price
                    
                    logger.info(f"Calculated prices - Min: {price_min}, Max: {price_max}, Exact: {estimated_price}")
                
                except (KeyError, ValueError, TypeError) as e:
                    logger.warning(f"Error getting price range from table: {str(e)}")
                    price_min = estimated_price
                    price_max = estimated_price
                
                return Response({
                    'estimated_price': float(estimated_price),
                    'price_min': float(price_min),
                    'price_max': float(price_max),
                })
            
            except Exception as e:
                logger.error(f"Error in price calculation logic: {str(e)}", exc_info=True)
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        else:
            logger.warning(f"Price calculation validation errors: {serializer.errors}")
            return Response(
                {'errors': serializer.errors, 'message': 'Ошибка валидации данных'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    except Exception as e:
        logger.error(f"Error calculating price: {str(e)}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    responses={200: PriceListSerializer(many=True)},
    description='Получить список активных цен'
)
@api_view(['GET'])
def price_list(request):
    """Get active price list."""
    try:
        prices = PriceList.objects.filter(is_active=True)
        serializer = PriceListSerializer(prices, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error getting price list: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Ошибка при получении списка цен'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
