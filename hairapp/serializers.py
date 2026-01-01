from rest_framework import serializers
from .models import HairApplication, PriceList
import logging

logger = logging.getLogger(__name__)


class HairApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for HairApplication model.
    Accepts data from new frontend:
    - hair_color: str (blonde, dark_blonde, light_brown, brown, dark_brown, black)
    - hair_length: int (40-150 cm)
    - hair_structure: str (slavyanka, european, asian)
    - hair_age: int (months, 0-120)
    - hair_condition: str (excellent, good, fair)
    - name: str
    - phone: str
    - email: str (optional)
    - city: str (optional)
    - comment: str (optional)
    """
    
    class Meta:
        model = HairApplication
        fields = [
            'hair_color',
            'hair_length',
            'hair_structure',
            'hair_age',
            'hair_condition',
            'name',
            'phone',
            'email',
        ]
        extra_kwargs = {
            'hair_color': {'required': True, 'allow_blank': False},
            'hair_length': {'required': True},
            'hair_structure': {'required': True, 'allow_blank': False},
            'hair_age': {'required': True},
            'hair_condition': {'required': True, 'allow_blank': False},
            'name': {'required': True, 'allow_blank': False},
            'phone': {'required': True, 'allow_blank': False},
            'email': {'required': False, 'allow_blank': True},
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields non-required by default for partial updates
        for field_name, field in self.fields.items():
            if hasattr(field, 'required'):
                # Keep required fields for create, allow partial for updates
                pass
    
    def validate_hair_length(self, value):
        """Validate hair length is between 40 and 150 cm"""
        if not isinstance(value, int):
            try:
                value = int(value)
            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    f"hair_length must be an integer, got {type(value).__name__}"
                )
        
        if value < 40 or value > 150:
            raise serializers.ValidationError(
                f"hair_length must be between 40 and 150 cm, got {value}"
            )
        return value
    
    def validate_hair_age(self, value):
        """Validate hair age in months"""
        if not isinstance(value, int):
            try:
                value = int(value)
            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    f"hair_age must be an integer, got {type(value).__name__}"
                )
        
        if value < 0 or value > 120:
            raise serializers.ValidationError(
                f"hair_age must be between 0 and 120 months, got {value}"
            )
        return value
    
    def validate_hair_color(self, value):
        """Validate hair color is one of allowed values"""
        allowed_colors = ['blonde', 'dark_blonde', 'light_brown', 'brown', 'dark_brown', 'black']
        if value not in allowed_colors:
            raise serializers.ValidationError(
                f"hair_color must be one of {allowed_colors}, got '{value}'"
            )
        return value
    
    def validate_hair_structure(self, value):
        """Validate hair structure is one of allowed values"""
        allowed_structures = ['slavyanka', 'european', 'asian']
        if value not in allowed_structures:
            raise serializers.ValidationError(
                f"hair_structure must be one of {allowed_structures}, got '{value}'"
            )
        return value
    
    def validate_hair_condition(self, value):
        """Validate hair condition is one of allowed values"""
        allowed_conditions = ['excellent', 'good', 'fair']
        if value not in allowed_conditions:
            raise serializers.ValidationError(
                f"hair_condition must be one of {allowed_conditions}, got '{value}'"
            )
        return value
    
    def validate_phone(self, value):
        """Validate phone number format"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("phone cannot be empty")
        return value.strip()
    
    def validate_name(self, value):
        """Validate name is not empty"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("name cannot be empty")
        return value.strip()
    
    def validate_email(self, value):
        """Validate email if provided"""
        if value and len(value.strip()) == 0:
            return None
        return value.strip() if value else None
    
    def create(self, validated_data):
        """Create HairApplication instance"""
        logger.info(f"Creating HairApplication with data: {validated_data}")
        
        # Create the application
        application = HairApplication.objects.create(**validated_data)
        
        logger.info(f"HairApplication created successfully with ID {application.id}")
        return application
    
    def to_representation(self, instance):
        """Return representation of the application"""
        return {
            'id': instance.id,
            'hair_color': instance.hair_color,
            'hair_length': instance.hair_length,
            'hair_structure': instance.hair_structure,
            'hair_age': instance.hair_age,
            'hair_condition': instance.hair_condition,
            'name': instance.name,
            'phone': instance.phone,
            'email': instance.email,
            'created_at': instance.created_at,
        }


class PriceCalculatorSerializer(serializers.Serializer):
    """
    Serializer for price calculation endpoint.
    """
    hair_color = serializers.CharField(required=True)
    hair_length = serializers.IntegerField(required=True)
    hair_structure = serializers.CharField(required=True)
    hair_age = serializers.IntegerField(required=False, allow_null=True, default=0)
    hair_condition = serializers.CharField(required=True)
    
    def validate_hair_length(self, value):
        if value < 40 or value > 150:
            raise serializers.ValidationError(
                "hair_length must be between 40 and 150 cm"
            )
        return value
    
    def validate_hair_age(self, value):
        if value is None:
            return 0
        if value < 0 or value > 120:
            raise serializers.ValidationError(
                "hair_age must be between 0 and 120 months"
            )
        return value
    
    def validate_hair_color(self, value):
        allowed_colors = ['blonde', 'dark_blonde', 'light_brown', 'brown', 'dark_brown', 'black']
        if value not in allowed_colors:
            raise serializers.ValidationError(
                f"hair_color must be one of {allowed_colors}"
            )
        return value
    
    def validate_hair_structure(self, value):
        allowed_structures = ['slavyanka', 'european', 'asian']
        if value not in allowed_structures:
            raise serializers.ValidationError(
                f"hair_structure must be one of {allowed_structures}"
            )
        return value
    
    def validate_hair_condition(self, value):
        allowed_conditions = ['excellent', 'good', 'fair']
        if value not in allowed_conditions:
            raise serializers.ValidationError(
                f"hair_condition must be one of {allowed_conditions}"
            )
        return value


class PriceListSerializer(serializers.ModelSerializer):
    """
    Serializer for PriceList model.
    """
    class Meta:
        model = PriceList
        fields = '__all__'
