import pytest
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from hair_app.serializers import HairApplicationSerializer


def create_test_image():
    """
    Create a temporary test image file.
    """
    file = BytesIO()
    image = Image.new('RGB', (100, 100), color='red')
    image.save(file, 'PNG')
    file.seek(0)
    return SimpleUploadedFile(
        name='test_image.png',
        content=file.getvalue(),
        content_type='image/png'
    )


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
            'email': 'test@example.com',
            'photo1': create_test_image(),  # ✅ ДОБАВИЛИ ОБЯЗАТЕЛЬНОЕ ФОТО
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
            'email': 'test@example.com',
            'photo1': create_test_image(),  # ✅ ДОБАВИЛИ ОБЯЗАТЕЛЬНОЕ ФОТО
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
            'email': 'invalid-email',  # ← Невалидная!
            'photo1': create_test_image(),  # ✅ ДОБАВИЛИ ОБЯЗАТЕЛЬНОЕ ФОТО
        }
        serializer = HairApplicationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors
    
    def test_missing_required_field(self):
        """Тест: отсутствующие обязательные поля"""
        data = {
            'color': 'блонд',
            'structure': 'славянка',
            # ← Отсутствуют length, age, condition, name, phone, photo1
        }
        serializer = HairApplicationSerializer(data=data)
        assert not serializer.is_valid()
        # Проверяем что регистрируются ошибки
        assert len(serializer.errors) >= 3
    
    def test_missing_photo1(self):
        """Тест: обязательное фото 1 отсутствует"""
        data = {
            'length': '100+',
            'color': 'блонд',
            'structure': 'славянка',
            'age': 'взрослые',
            'condition': 'натуральные',
            'name': 'Test',
            'phone': '+7 (911) 957-17-12',
            'email': 'test@example.com',
            # ← photo1 НЕ ОТПРАВЛЕНО!
        }
        serializer = HairApplicationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'photo1' in serializer.errors
    
    def test_optional_photos(self):
        """Тест: photo2 и photo3 опциональны"""
        data = {
            'length': '100+',
            'color': 'блонд',
            'structure': 'славянка',
            'age': 'взрослые',
            'condition': 'натуральные',
            'name': 'Test',
            'phone': '+7 (911) 957-17-12',
            'email': 'test@example.com',
            'photo1': create_test_image(),
            # photo2 и photo3 НЕ ОТПРАВЛЕНЫ - должно быть OK
        }
        serializer = HairApplicationSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
