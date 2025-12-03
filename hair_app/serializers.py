"""
DRF Serializers for hair purchase application
"""
from rest_framework import serializers
from .models import HairApplication, PriceList


class HairApplicationSerializer(serializers.ModelSerializer):
    """Serializer for hair applications."""
    
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


class PriceCalculatorSerializer(serializers.Serializer):
    """Serializer for price calculation."""
    
    length = serializers.ChoiceField(choices=HairApplication.LENGTH_CHOICES)
    color = serializers.ChoiceField(choices=HairApplication.COLOR_CHOICES)
    structure = serializers.ChoiceField(choices=HairApplication.STRUCTURE_CHOICES)
    age = serializers.ChoiceField(choices=HairApplication.AGE_CHOICES)  # ДОБАВЛЕНО
    condition = serializers.ChoiceField(choices=HairApplication.CONDITION_CHOICES)
    

class PriceListSerializer(serializers.ModelSerializer):
    """Serializer for price list."""
    
    class Meta:
        model = PriceList
        fields = [
            'id', 'length', 'color', 'structure', 'condition',
            'base_price', 'is_active',
            'created_at', 'updated_at'
        ]
