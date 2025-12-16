import pytest
from rest_framework.test import APITestCase
from hair_app.serializers import HairApplicationSerializer


class TestHairApplicationSerializer(APITestCase):
    """Тесты сериалайзера"""
    
    def test_valid_data(self):
        """Тест: валидные данные принимаются"""
        data = {
            'length': '100+',
            'color': 'блонд',
            'structure': 'славянка',
            'age': 'взрослые',
            'condition': 'натуральные',
            'name': 'Test',
            'phone': '+7 (911) 957-17-12',
            'email': 'test@example.com'
        }
        serializer = HairApplicationSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
    
    def test_invalid_phone(self):
        """Тест: невалидный телефон отклоняется"""
        data = {
            'length': '100+',
            'color': 'блонд',
            'structure': 'славянка',
            'age': 'взрослые',
            'condition': 'натуральные',
            'name': 'Test',
            'phone': '123456',  # ← Неверный формат!
            'email': 'test@example.com'
        }
        serializer = HairApplicationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'phone' in serializer.errors
    
    def test_invalid_email(self):
        """Тест: невалидная почта отклоняется"""
        data = {
            'length': '100+',
            'color': 'блонд',
            'structure': 'славянка',
            'age': 'взрослые',
            'condition': 'натуральные',
            'name': 'Test',
            'phone': '+7 (911) 957-17-12',
            'email': 'invalid-email'  # ← Невалидная!
        }
        serializer = HairApplicationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors
    
    def test_missing_required_field(self):
        """Тест: отсутствующие обязательные поля"""
        data = {
            'color': 'блонд',
            'structure': 'славянка',
            # ← Отсутствуют length, age, condition, name, phone
        }
        serializer = HairApplicationSerializer(data=data)
        assert not serializer.is_valid()
        # Проверяем что расстраиваются не менее 3 наносов
        assert len(serializer.errors) >= 3
