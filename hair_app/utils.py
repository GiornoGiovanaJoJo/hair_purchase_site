"""
Utility functions for hair purchase application
"""
from decimal import Decimal
from .price_calculator import calculate_hair_price as calc_price


def calculate_hair_price(length, color, structure, age, condition):
    """
    Calculate hair price based on characteristics.
    
    This function wraps the price_calculator.calculate_hair_price function.
    
    Args:
        length: Hair length in cm (40-150)
        color: Hair color (e.g., 'blonde', 'light_brown', 'brown', 'dark_brown', 'chestnut', 'black')
        structure: Hair structure (e.g., 'slavic', 'average', 'thick')
        age: Hair age category (e.g., 'adult', 'child') - NOT USED in calculation
        condition: Hair condition (e.g., 'natural', 'dyed', 'perm')
    
    Returns:
        int: Calculated price in rubles
    
    Examples:
        >>> calculate_hair_price(60, 'blonde', 'slavic', 'adult', 'natural')
        35000
        
        >>> calculate_hair_price(60, 'blonde', 'average', 'adult', 'natural')
        31500
    """
    try:
        # Convert length to integer if needed
        if isinstance(length, str):
            # Parse length range if it's like "50-60"
            if '-' in str(length):
                length = int(str(length).split('-')[0])
            else:
                length = int(length)
        else:
            length = int(length)
        
        # Normalize color names (support both English and Russian)
        color_mapping = {
            # English
            'blonde': 'blonde',
            'light_brown': 'light_brown',
            'light brown': 'light_brown',
            'brown': 'brown',
            'dark_brown': 'dark_brown',
            'dark brown': 'dark_brown',
            'chestnut': 'chestnut',
            'black': 'black',
            # Russian
            'блонд': 'blonde',
            'светло-русые': 'light_brown',
            'русые': 'brown',
            'темно-русые': 'dark_brown',
            'каштановые': 'chestnut',
            'черные': 'black',
        }
        color = color_mapping.get(str(color).strip().lower(), 'blonde')
        
        # Normalize structure names
        structure_mapping = {
            # English
            'slavic': 'slavic',
            'average': 'average',
            'thick': 'thick',
            # Russian
            'славянка': 'slavic',
            'среднее': 'average',
            'густые': 'thick',
        }
        structure = structure_mapping.get(str(structure).strip().lower(), 'average')
        
        # Normalize condition names
        condition_mapping = {
            # English
            'natural': 'natural',
            'dyed': 'dyed',
            'perm': 'perm',
            # Russian
            'натуральные': 'natural',
            'окрашенные': 'dyed',
            'после химии': 'perm',
        }
        condition = condition_mapping.get(str(condition).strip().lower(), 'natural')
        
        # Calculate price using the new price calculator
        price = calc_price(
            length=length,
            color=color,
            structure=structure,
            condition=condition,
            age=age  # age is ignored in price_calculator
        )
        
        return int(price)
        
    except Exception as e:
        # Return a default price if calculation fails
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error calculating hair price: {e}', exc_info=True)
        return 30000  # Safe default value
