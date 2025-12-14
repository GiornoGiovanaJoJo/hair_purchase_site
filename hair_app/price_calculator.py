# -*- coding: utf-8 -*-
"""
Калькулятор цены волос для скупки

Рассчитывает стоимость волос на основе:
- Длины (5 диапазонов)
- Цвета (влияет на стоимость)
- Состояния (натуральные дороже всего)

Использование:
    price = calculate_hair_price(
        length=50,  # см
        color='блонд',
        condition='натуральное'
    )
"""

# ============================================
# ТАБЛИЦА БАЗ ОВЫХ ЦЕН ПО ДЛИНЕ
# ============================================

BASE_PRICES = {
    # (min_length, max_length): (cheap, medium, expensive)
    # Дешевые - густые/вьющиеся
    # Средние - средняя структура
    # Дорогие - славянка/здоровые
    (40, 50): {'cheap': 20000, 'medium': 22000, 'expensive': 25000},
    (50, 60): {'cheap': 28000, 'medium': 30000, 'expensive': 35000},
    (60, 80): {'cheap': 38000, 'medium': 40000, 'expensive': 45000},
    (80, 100): {'cheap': 48000, 'medium': 50000, 'expensive': 55000},
    (100, 150): {'cheap': 55000, 'medium': 60000, 'expensive': 65000},
}

# ============================================
# КОЭФФИЦИЕНТЫ ПО ЦВЕТУ ВОЛОС
# ============================================

COLOR_MULTIPLIERS = {
    # Светлые волосы дороже (много на рынке)
    'блонд': 1.0,  # базовая цена
    'светло-русые': 0.95,
    'русые': 0.90,
    'темно-русые': 0.88,
    'каштановые': 0.85,  # коричневые волосы дешевле
    'черные': 0.80,  # черные - самые дешевые
}

# ============================================
# КОЭФФИЦИЕНТЫ ПО СОСТОЯНИЮ ВОЛОС
# ============================================

CONDITION_MULTIPLIERS = {
    # Натуральные волосы дороже всего
    'натуральные': 1.15,  # +15% к базовой цене
    'окрашенные': 0.85,   # -15% (волосы повреждены)
    'после химии': 0.75,  # -25% (значительно повреждены)
}

# ============================================
# КОЭФФИЦИЕНТЫ ПО СТРУКТУРЕ ВОЛОС
# ============================================

STRUCTURE_MULTIPLIERS = {
    # Тип волос влияет на цену
    'славянка': 1.10,      # +10% (лучше всего)
    'среднее': 1.0,        # базовая цена
    'густые': 0.95,        # -5% (тяжелые для работы)
    'вьющиеся': 0.90,      # -10% (нужна специальная обработка)
}

# ============================================
# ВОЗРАСТНОЙ КОЭФФИЦИЕНТ
# ============================================

AGE_MULTIPLIERS = {
    'детские': 1.05,   # +5% (тонкие, редкие волосы дороже)
    'взрослые': 1.0,   # базовая цена
}


# ============================================
# ОСНОВНАЯ ФУНКЦИЯ РАСЧЕТА
# ============================================

def calculate_hair_price(
    length: int,
    color: str = 'блонд',
    condition: str = 'натуральные',
    structure: str = 'среднее',
    age: str = 'взрослые'
) -> int:
    """
    Рассчитывает цену волос на основе параметров.
    
    Args:
        length (int): Длина волос в сантиметрах (40-150)
        color (str): Цвет волос (блонд, русые, черные и т.д.)
        condition (str): Состояние (натуральные, окрашенные, после химии)
        structure (str): Структура (славянка, среднее, густые, вьющиеся)
        age (str): Возраст (детские, взрослые)
    
    Returns:
        int: Рассчитанная цена в рублях
    
    Примеры:
        >>> calculate_hair_price(50, 'блонд', 'натуральные', 'славянка')
        25750  # 50-60 см, дорогие волосы, блонд, натуральные, славянка
        
        >>> calculate_hair_price(80, 'черные', 'окрашенные', 'вьющиеся')
        30800  # 80-100 см, дешевые волосы, черные, окрашенные, вьющиеся
    """
    
    # Нормализуем входные данные
    length = int(length) if length else 50
    color = color.strip().lower() if color else 'блонд'
    condition = condition.strip().lower() if condition else 'натуральные'
    structure = structure.strip().lower() if structure else 'среднее'
    age = age.strip().lower() if age else 'взрослые'
    
    # Обработка диапазонов длины
    if length < 40:
        length = 40  # Минимум 40 см
    elif length > 150:
        length = 150  # Максимум 150 см
    
    # Шаг 1: Находим базовую цену по длине
    base_price = None
    price_category = 'medium'  # по умолчанию средняя
    
    for (min_len, max_len), prices in BASE_PRICES.items():
        if min_len <= length <= max_len:
            # Определяем категорию волос по качеству
            if condition == 'натуральные' and structure == 'славянка':
                price_category = 'expensive'
            elif condition in ['окрашенные', 'после химии'] or structure == 'вьющиеся':
                price_category = 'cheap'
            else:
                price_category = 'medium'
            
            base_price = prices[price_category]
            break
    
    if base_price is None:
        # Если не найдено в таблице, интерполируем
        base_price = 50000  # Дефолтная цена
    
    # Шаг 2: Применяем коэффициент по цвету
    color_multiplier = COLOR_MULTIPLIERS.get(color, 1.0)
    price_after_color = base_price * color_multiplier
    
    # Шаг 3: Применяем коэффициент по состоянию
    condition_multiplier = CONDITION_MULTIPLIERS.get(condition, 1.0)
    price_after_condition = price_after_color * condition_multiplier
    
    # Шаг 4: Применяем коэффициент по структуре
    # (если не был учтен в выборе категории)
    if structure not in ['славянка', 'вьющиеся']:
        structure_multiplier = STRUCTURE_MULTIPLIERS.get(structure, 1.0)
        price_after_structure = price_after_condition * structure_multiplier
    else:
        price_after_structure = price_after_condition
    
    # Шаг 5: Применяем коэффициент по возрасту
    age_multiplier = AGE_MULTIPLIERS.get(age, 1.0)
    final_price = price_after_structure * age_multiplier
    
    # Округляем до целого числа
    return int(round(final_price))


# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def get_price_range(length: int) -> dict:
    """
    Возвращает диапазон цен для заданной длины волос.
    
    Args:
        length (int): Длина в сантиметрах
    
    Returns:
        dict: {'min': цена, 'max': цена, 'range': 'X-Y см'}
    """
    for (min_len, max_len), prices in BASE_PRICES.items():
        if min_len <= length <= max_len:
            return {
                'min': prices['cheap'],
                'max': prices['expensive'],
                'range': f'{min_len}-{max_len} см',
                'medium': prices['medium']
            }
    
    return {
        'min': 20000,
        'max': 65000,
        'range': '40-150 см',
        'medium': 40000
    }


def estimate_price_variations(length: int, color: str = 'блонд') -> dict:
    """
    Рассчитывает вариации цены для всех состояний.
    
    Args:
        length (int): Длина волос
        color (str): Цвет волос
    
    Returns:
        dict: Ценовые вариации для разных состояний
    """
    variations = {}
    
    for condition in CONDITION_MULTIPLIERS.keys():
        for structure in STRUCTURE_MULTIPLIERS.keys():
            key = f"{condition} ({structure})"
            variations[key] = calculate_hair_price(
                length=length,
                color=color,
                condition=condition,
                structure=structure
            )
    
    return variations


# ============================================
# ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ
# ============================================

if __name__ == '__main__':
    print("=" * 60)
    print("ПРИМЕРЫ РАСЧЕТА ЦЕНЫ ВОЛОС")
    print("=" * 60)
    
    # Пример 1: Дорогие волосы
    price1 = calculate_hair_price(
        length=60,
        color='блонд',
        condition='натуральные',
        structure='славянка',
        age='взрослые'
    )
    print(f"\n1. Блонд, 60 см, натуральные, славянка: {price1:,} ₽")
    
    # Пример 2: Средние волосы
    price2 = calculate_hair_price(
        length=50,
        color='русые',
        condition='натуральные',
        structure='среднее',
        age='взрослые'
    )
    print(f"2. Русые, 50 см, натуральные, среднее: {price2:,} ₽")
    
    # Пример 3: Дешевые волосы
    price3 = calculate_hair_price(
        length=80,
        color='черные',
        condition='окрашенные',
        structure='вьющиеся',
        age='взрослые'
    )
    print(f"3. Черные, 80 см, окрашенные, вьющиеся: {price3:,} ₽")
    
    # Пример 4: Длинные волосы
    price4 = calculate_hair_price(
        length=120,
        color='светло-русые',
        condition='натуральные',
        structure='славянка',
        age='взрослые'
    )
    print(f"4. Светло-русые, 120 см, натуральные, славянка: {price4:,} ₽")
    
    # Пример 5: Детские волосы
    price5 = calculate_hair_price(
        length=45,
        color='блонд',
        condition='натуральные',
        structure='среднее',
        age='детские'
    )
    print(f"5. Блонд, 45 см, натуральные, средние (детские): {price5:,} ₽")
    
    # Пример 6: Диапазон цен
    print(f"\n\nДИАПАЗОНЫ ЦЕН ПО ДЛИНЕ:")
    for length in [45, 55, 70, 90, 120]:
        range_info = get_price_range(length)
        print(f"{range_info['range']}: {range_info['min']:,} - {range_info['max']:,} ₽")
