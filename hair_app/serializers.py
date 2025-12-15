"""
DRF Serializers for hair purchase application
"""
import logging
from rest_framework import serializers
from .models import HairApplication, PriceList, normalize_phone

logger = logging.getLogger(__name__)


class HairApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for hair applications.
    """
    
    # 🔧 CRITICAL FIX: photo2 and photo3 should allow empty (not provide them if empty)
    photo2 = serializers.ImageField(required=False, allow_null=True)
    photo3 = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = HairApplication
        fields = [
            'id', 'length', 'color', 'structure', 'age', 'condition',
            'photo1', 'photo2', 'photo3',
            'name', 'phone', 'email', 'city', 'comment',
            'estimated_price', 'final_price', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'estimated_price', 'final_price', 'status', 'created_at', 'updated_at']
    
    def validate_phone(self, value):
        """
        ✅ НОРМАЛИЗИРУЕМ ТЕЛЕФОН ПЕРЕД ВАЛИДАЦИЕЙ!
        Принимаем ЛЮБОЙ формат и конвертируем в +7 (999) 123-45-67
        """
        if not value:
            raise serializers.ValidationError('Телефон должен быть указан')
        
        logger.info(f"🔧 validate_phone() called with value: '{value}' (type: {type(value).__name__})")
        
        # ✅ НОРМАЛИЗИРУЕМ ТЕЛЕФОН ИСПОЛЬЗОВАНИЕМ ФУНКЦИИ ИЗ MODELS!
        normalized = normalize_phone(value)
        logger.info(f"🔧 normalize_phone('{value}') returned: '{normalized}'")
        
        # Проверяем что нормализация прошла успешно
        digits = ''.join(c for c in str(normalized) if c.isdigit())
        logger.info(f"🔧 extracted digits: '{digits}' (count: {len(digits)})")
        
        if len(digits) != 11:
            logger.error(f"🔧 ERROR: Phone has {len(digits)} digits, expected 11")
            raise serializers.ValidationError(
                'Телефон должен содержать 11 цифр. '
                'Отправьте: +7 999 123 45 67'
            )
        
        if not digits.startswith('7'):
            logger.error(f"🔧 ERROR: Phone doesn't start with 7, digits: {digits}")
            raise serializers.ValidationError(
                'Телефон должен начинаться с +7. '
                'Отправьте: +7 999 123 45 67'
            )
        
        # Возвращаем НОРМАЛИЗИРОВАННЫЙ телефон!
        logger.info(f"🔧 validate_phone() returning normalized: '{normalized}'")
        return normalized
    
    def validate_name(self, value):
        """
        Валидируем имя.
        """
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError('Имя должно состоять минимум из 2 символов')
        
        return value.strip()
    
    def validate_photo1(self, value):
        """
        Валидируем ОБАЗАТЕЛЬНОЕ фото 1.
        """
        if not value:
            raise serializers.ValidationError(
                'Обязательно загружайте минимум 1 фото ("Фото 1")'
            )
        
        # Проверяем размер (не больше 10 МБ)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('Файл слишком большой (макс 10 МБ)')
        
        return value
    
    def validate(self, data):
        """
        Общая валидация.
        """
        logger.info(f"🔧 validate() called with validated_data keys: {data.keys()}")
        logger.info(f"🔧 phone value in data: '{data.get('phone')}'")
        
        # Проверяем все обязательные селекты
        required_fields = ['length', 'color', 'structure', 'age', 'condition', 'name', 'phone', 'photo1']
        missing = [f for f in required_fields if not data.get(f)]
        
        if missing:
            logger.error(f"🔧 Missing required fields: {missing}")
            raise serializers.ValidationError(
                f'Обязательные поля не выполнены: {", ".join(missing)}'
            )
        
        return data


class PriceCalculatorSerializer(serializers.Serializer):
    """
    Serializer for price calculation.
    """
    
    length = serializers.ChoiceField(choices=HairApplication.LENGTH_CHOICES)
    color = serializers.ChoiceField(choices=HairApplication.COLOR_CHOICES)
    structure = serializers.ChoiceField(choices=HairApplication.STRUCTURE_CHOICES)
    age = serializers.ChoiceField(
        choices=HairApplication.AGE_CHOICES,
        required=False,
        allow_blank=True,
        help_text='Опционально. Если не указано, используется значение по умолчанию (взрослые)'
    )
    condition = serializers.ChoiceField(choices=HairApplication.CONDITION_CHOICES)
    
    def validate(self, data):
        """
        Если age не передан или пуст, используем default значение.
        """
        if not data.get('age') or data.get('age') == '':
            # Default значение для age если не передан
            data['age'] = 'взрослые'
        return data


class PriceListSerializer(serializers.ModelSerializer):
    """
    Serializer for price list.
    """
    
    class Meta:
        model = PriceList
        fields = [
            'id', 'length', 'color', 'structure', 'condition',
            'base_price', 'is_active',
            'created_at', 'updated_at'
        ]
