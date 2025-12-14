# -*- coding: utf-8 -*-
"""
Калькулятор цены волос для скупки

Рассчитывает стоимость волос на основе:
- Длины (5 диапазонов)
- Цвета волос (разные базовые цены)
- Структуры волос (модификаторы)
- Состояния волос (модификаторы)

Формула расчета:
    ЦЕНА = БАЗА (из таблицы) × МОДИФИКАТОР_СТРУКТУРЫ × МОДИФИКАТОР_СОСТОЯНИЯ

Использование:
    price = calculate_hair_price(
        length=60,  # см
        color='blonde',
        structure='slavic',
        condition='natural'
    )
"""

# ============================================
# ТАБЛИЦА БАЗОВЫХ ЦЕН (максимум для Славянки)
# ============================================

PRICE_TABLE = {
    'blonde': {
        '40-50': 25000,
        '50-60': 35000,
        '60-80': 45000,
        '80-100': 55000,
        '100+': 65000,
    },
    'light_brown': {
        '40-50': 20000,
        '50-60': 25000,
        '60-80': 35000,
        '80-100': 45000,
        '100+': 55000,
    },
    'brown': {
        '40-50': 18000,
        '50-60': 20000,
        '60-80': 30000,
        '80-100': 40000,
        '100+': 50000,
    },
    'dark_brown': {
        '40-50': 18000,
        '50-60': 20000,
        '60-80': 30000,
        '80-100': 40000,
        '100+': 50000,
    },
    'chestnut': {
        '40-50': 20000,
        '50-60': 25000,
        '60-80': 35000,
        '80-100': 45000,
        '100+': 55000,
    },
    'black': {
        '40-50': 18000,
        '50-60': 20000,
        '60-80': 30000,
        '80-100': 40000,
        '100+': 50000,
    },
}

# ============================================
# МОДИФИКАТОРЫ СТРУКТУРЫ (понижают цену)
# ============================================

STRUCTURE_MODIFIERS = {
    'slavic': 1.0,      # 0% понижения (максимум)
    'average': 0.9,     # 10% понижения
    'thick': 0.8,       # 20% понижения
}

# ============================================
# МОДИФИКАТОРЫ СОСТОЯНИЯ (понижают цену)
# ============================================

CONDITION_MODIFIERS = {
    'natural': 1.0,     # 0% понижения (максимум)
    'dyed': 0.7,        # 30% понижения
    'perm': 0.5,        # 50% понижения (химическая завивка)
}


# ============================================
# ОСНОВНАЯ ФУНКЦИЯ РАСЧЕТА
# ============================================

def calculate_hair_price(
    length: int,
    color: str = 'blonde',
    structure: str = 'average',
    condition: str = 'natural',
    age: str = 'adult'  # НЕ ИСПОЛЬЗУЕТСЯ, оставлен для совместимости
) -> int:
    """
    Рассчитывает цену волос на основе таблицы и модификаторов.
    
    Формула:
        ЦЕНА = БАЗА × МОДИФИКАТОР_СТРУКТУРЫ × МОДИФИКАТОР_СОСТОЯНИЯ
    
    Args:
        length (int): Длина волос в сантиметрах (40-150)
        color (str): Цвет волос
            - 'blonde' (блонд)
            - 'light_brown' (светло-русые)
            - 'brown' (русые)
            - 'dark_brown' (темно-русые)
            - 'chestnut' (каштановые)
            - 'black' (черные)
        structure (str): Структура волос
            - 'slavic' (славянка)
            - 'average' (среднее)
            - 'thick' (густые)
        condition (str): Состояние волос
            - 'natural' (натуральные)
            - 'dyed' (окрашенные)
            - 'perm' (после химии/завивки)
        age (str): Возраст (НЕ ИСПОЛЬЗУЕТСЯ)
    
    Returns:
        int: Рассчитанная цена в рублях
    
    Примеры:
        >>> calculate_hair_price(60, 'blonde', 'slavic', 'natural')
        35000  # Блонд, 60см, славянка, натуральные
        
        >>> calculate_hair_price(60, 'blonde', 'average', 'natural')
        31500  # Блонд, 60см, среднее, натуральные
        
        >>> calculate_hair_price(60, 'blonde', 'thick', 'natural')
        28000  # Блонд, 60см, густые, натуральные
    """
    
    # Нормализуем входные данные
    length = int(length) if length else 50
    color = str(color).strip().lower() if color else 'blonde'
    structure = str(structure).strip().lower() if structure else 'average'
    condition = str(condition).strip().lower() if condition else 'natural'
    
    # Обработка диапазонов длины
    if length < 40:
        length = 40
    elif length > 150:
        length = 150
    
    # 1. Определяем диапазон длины
    if length < 50:
        length_range = '40-50'
    elif length < 60:
        length_range = '50-60'
    elif length < 80:
        length_range = '60-80'
    elif length < 100:
        length_range = '80-100'
    else:
        length_range = '100+'
    
    # 2. Берём базовую цену из таблицы
    try:
        base_price = PRICE_TABLE[color][length_range]
    except KeyError:
        # Если цвет неправильный, используем блонд как дефолт
        base_price = PRICE_TABLE['blonde'][length_range]
    
    # 3. Применяем модификатор структуры
    structure_modifier = STRUCTURE_MODIFIERS.get(structure, 1.0)
    price_after_structure = base_price * structure_modifier
    
    # 4. Применяем модификатор состояния
    condition_modifier = CONDITION_MODIFIERS.get(condition, 1.0)
    final_price = price_after_structure * condition_modifier
    
    # Округляем до целого числа
    return int(round(final_price))


# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def get_color_options():
    """Возвращает список доступных цветов волос."""
    return {
        'blonde': 'Блонд',
        'light_brown': 'Светло-русые',
        'brown': 'Русые',
        'dark_brown': 'Темно-русые',
        'chestnut': 'Каштановые',
        'black': 'Чёрные',
    }


def get_structure_options():
    """Возвращает список доступных структур волос."""
    return {
        'slavic': 'Славянка',
        'average': 'Среднее',
        'thick': 'Густые',
    }


def get_condition_options():
    """Возвращает список доступных состояний волос."""
    return {
        'natural': 'Натуральные',
        'dyed': 'Окрашенные',
        'perm': 'После химии',
    }


def get_price_range(length: int):
    """
    Возвращает диапазон цен для заданной длины волос (все цвета).
    
    Args:
        length (int): Длина в сантиметрах
    
    Returns:
        dict: Информация о диапазоне цен
    """
    # Определяем диапазон длины
    if length < 50:
        length_range = '40-50'
    elif length < 60:
        length_range = '50-60'
    elif length < 80:
        length_range = '60-80'
    elif length < 100:
        length_range = '80-100'
    else:
        length_range = '100+'
    
    # Собираем минимум и максимум по всем цветам
    min_price = float('inf')
    max_price = 0
    
    for color_prices in PRICE_TABLE.values():
        price = color_prices[length_range]
        min_price = min(min_price, price)
        max_price = max(max_price, price)
    
    return {
        'min': int(min_price),
        'max': int(max_price),
        'range': length_range,
    }


# ============================================
# ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ
# ============================================

if __name__ == '__main__':
    print("=" * 70)
    print("ПРИМЕРЫ РАСЧЕТА ЦЕНЫ ВОЛОС (ПО ПРАВИЛЬНОЙ ТАБЛИЦЕ)")
    print("=" * 70)
    
    # Пример 1: Максимум - Блонд, славянка, натуральные
    price1 = calculate_hair_price(60, 'blonde', 'slavic', 'natural')
    print(f"\n1. Блонд, 60см, славянка, натуральные")
    print(f"   35,000 × 1.0 × 1.0 = {price1:,} ₽")
    
    # Пример 2: Блонд, среднее качество
    price2 = calculate_hair_price(60, 'blonde', 'average', 'natural')
    print(f"\n2. Блонд, 60см, среднее, натуральные")
    print(f"   35,000 × 0.9 × 1.0 = {price2:,} ₽")
    
    # Пример 3: Блонд, густые
    price3 = calculate_hair_price(60, 'blonde', 'thick', 'natural')
    print(f"\n3. Блонд, 60см, густые, натуральные")
    print(f"   35,000 × 0.8 × 1.0 = {price3:,} ₽")
    
    # Пример 4: Светло-русые, окрашенные
    price4 = calculate_hair_price(60, 'light_brown', 'slavic', 'dyed')
    print(f"\n4. Светло-русые, 60см, славянка, окрашенные")
    print(f"   25,000 × 1.0 × 0.7 = {price4:,} ₽")
    
    # Пример 5: Русые, после химии
    price5 = calculate_hair_price(60, 'brown', 'average', 'perm')
    print(f"\n5. Русые, 60см, среднее, после химии")
    print(f"   20,000 × 0.9 × 0.5 = {price5:,} ₽")
    
    # Пример 6: Черные, длинные, разные структуры
    print(f"\n6. Черные волосы, 80см (разные структуры):")
    for structure in ['slavic', 'average', 'thick']:
        price = calculate_hair_price(80, 'black', structure, 'natural')
        print(f"   - {structure}: {price:,} ₽")
    
    print("\n" + "=" * 70)
