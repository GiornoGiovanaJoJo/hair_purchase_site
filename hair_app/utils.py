"""
Utility functions for hair purchase application
"""
from decimal import Decimal
from .price_calculator import calculate_hair_price as calc_price


def calculate_hair_price(length, color, structure, age, condition):
    """
    Calculate hair price based on characteristics using exact table.
    
    This function wraps the price_calculator.calculate_hair_price function
    which uses a precise lookup table with 75 unique price combinations.
    
    Args:
        length: Hair length in cm (40-150) or range string like '50-60'
        color: Hair color in Russian (e.g., 'блонд', 'русые')
        structure: Hair structure in Russian ('славянка', 'среднее', 'густые')
        age: Hair age category - NOT USED in new calculator (kept for compatibility)
        condition: Hair condition - NOT USED in new calculator (kept for compatibility)
    
    Returns:
        int: Exact price in rubles from lookup table
    
    Examples:
        >>> calculate_hair_price(60, 'блонд', 'славянка', 'adult', 'natural')
        35000
        
        >>> calculate_hair_price(60, 'блонд', 'среднее', 'adult', 'natural')
        30000
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
        
        # Call the exact price calculator
        price = calc_price(
            length=length,
            color=color,
            structure=structure,
            condition=condition,
            age=age
        )
        
        return int(price)
        
    except Exception as e:
        # Return a safe default if calculation fails
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error calculating hair price: {e}', exc_info=True)
        return 30000  # Safe default value
