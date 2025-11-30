"""
Utility functions for hair purchase application
"""
from decimal import Decimal
from .models import PriceList


def calculate_hair_price(length, color, structure, condition):
    """
    Calculate hair price based on characteristics.
    
    Args:
        length: Hair length category
        color: Hair color category
        structure: Hair structure category
        condition: Hair condition category
    
    Returns:
        Decimal: Estimated price
    """
    try:
        # Try to find exact match in price list
        price_entry = PriceList.objects.filter(
            length=length,
            color=color,
            structure=structure,
            condition=condition,
            is_active=True
        ).first()
        
        if price_entry:
            return price_entry.base_price
        
        # If no exact match, calculate based on base multipliers
        base_price = Decimal('5000.00')
        
        # Length multiplier
        length_multipliers = {
            '40-50': Decimal('0.7'),
            '50-60': Decimal('0.85'),
            '60-70': Decimal('1.0'),
            '70-80': Decimal('1.2'),
            '80-90': Decimal('1.4'),
            '90-100': Decimal('1.6'),
            '100+': Decimal('1.8'),
        }
        
        # Color multiplier
        color_multipliers = {
            'blonde': Decimal('1.3'),
            'light': Decimal('1.2'),
            'medium': Decimal('1.0'),
            'dark': Decimal('0.9'),
            'brown': Decimal('0.8'),
        }
        
        # Structure multiplier
        structure_multipliers = {
            'thin': Decimal('1.2'),
            'medium': Decimal('1.0'),
            'thick': Decimal('0.9'),
        }
        
        # Condition multiplier
        condition_multipliers = {
            'natural': Decimal('1.0'),
            'dyed': Decimal('0.7'),
            'perm': Decimal('0.5'),
        }
        
        # Calculate final price
        price = base_price
        price *= length_multipliers.get(length, Decimal('1.0'))
        price *= color_multipliers.get(color, Decimal('1.0'))
        price *= structure_multipliers.get(structure, Decimal('1.0'))
        price *= condition_multipliers.get(condition, Decimal('1.0'))
        
        # Round to 2 decimal places
        return price.quantize(Decimal('0.01'))
        
    except Exception as e:
        # Return default price if calculation fails
        return Decimal('5000.00')
