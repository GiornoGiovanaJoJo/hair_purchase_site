import pytest
from django.test import TestCase
from hair_app.models import HairApplication, normalize_phone, PriceList


class TestNormalizePhone:
    """Тесты функции нормализации телефона"""
    
    def test_normalize_phone_with_plus(self):
        """Тест: +79119571712 → +7 (911) 957-17-12"""
        result = normalize_phone('+79119571712')
        assert result == '+7 (911) 957-17-12'
    
    def test_normalize_phone_with_8(self):
        """Тест: 89119571712 → +7 (911) 957-17-12"""
        result = normalize_phone('89119571712')
        assert result == '+7 (911) 957-17-12'
    
    def test_normalize_phone_with_spaces(self):
        """Тест: +7 911 957 17 12 → +7 (911) 957-17-12"""
        result = normalize_phone('+7 911 957 17 12')
        assert result == '+7 (911) 957-17-12'
    
    def test_normalize_phone_formatted(self):
        """Тест: +7 (911) 957-17-12 → +7 (911) 957-17-12"""
        result = normalize_phone('+7 (911) 957-17-12')
        assert result == '+7 (911) 957-17-12'


@pytest.mark.django_db
class TestHairApplicationModel:
    """Тесты модели HairApplication"""
    
    def test_create_application(self):
        """Тест создания заявки"""
        app = HairApplication.objects.create(
            length='100+',
            color='блонд',
            structure='славянка',
            age='взрослые',
            condition='натуральные',
            name='Test User',
            phone='+7 (911) 957-17-12',
            email='test@example.com',
            estimated_price=50000
        )
        
        assert app.status == 'new'
        assert app.estimated_price == 50000
        assert app.phone == '+7 (911) 957-17-12'
        assert 'Заявка' in str(app)
        assert 'Test User' in str(app)
    
    def test_phone_normalization_on_save(self):
        """Тест: телефон нормализуется при сохранении"""
        app = HairApplication.objects.create(
            length='100+',
            color='блонд',
            structure='славянка',
            age='взрослые',
            condition='натуральные',
            name='Test',
            phone='+79119571712',  # ← Без маски!
            estimated_price=50000
        )
        
        app.refresh_from_db()
        assert app.phone == '+7 (911) 957-17-12'  # ← С маской!
    
    def test_application_queryset_ordering(self):
        """Тест: заявки сортируются по дате"""
        app1 = HairApplication.objects.create(
            length='100+', color='блонд', structure='славянка',
            age='взрослые', condition='натуральные',
            name='App 1', phone='+7 (911) 111-11-11'
        )
        app2 = HairApplication.objects.create(
            length='100+', color='блонд', structure='славянка',
            age='взрослые', condition='натуральные',
            name='App 2', phone='+7 (922) 222-22-22'
        )
        
        apps = list(HairApplication.objects.all())
        assert apps[0] == app2  # Новая сверху
        assert apps[1] == app1
    
    def test_estimated_price_default(self):
        """Тест: стандартная цена заявки"""
        app = HairApplication.objects.create(
            length='100+',
            color='блонд',
            structure='славянка',
            age='взрослые',
            condition='натуральные',
            name='Test',
            phone='+7 (911) 957-17-12'
        )
        
        # Первоначальная цена должна быть None или 0
        assert app.estimated_price is None or app.estimated_price == 0
