# Hair Purchase Site

## Новый современный дизайн (2025-11)

Добавлен красивый аниме-стиль лендинг с плавной анимацией, навигацией по разделам и адаптивным интерфейсом.

**Визуальные секции:**
- Главная страница с крупным баннером и преимуществами
- Калькулятор стоимости
- Форма заявки на продажу волос
- Боковое меню для удобной навигации
- Адаптивные точки переключения разделов

**Старт:**

- Главная страница: `templates/index.html`
- Стили: `static/css/style.css`
- JS: `static/js/main.js`
- При отсутствии `hero.jpg` используется SVG-заглушка

Сайт совместим с Django 5.2+.

---

## Описание проекта

Одностраничный сайт для приема заявок на продажу натуральных волос с калькулятором стоимости и формой обратной связи.

### Основные возможности:
- Калькулятор стоимости волос (длина, цвет, структура)
- Форма заявки с загрузкой фото
- Интеграция с Яндекс.Метрикой
- Telegram бот для управления заявками
- Админ-панель Django

## Технологии
- Python 3.12
- Django 5.2.8 (LTS)
- Django REST Framework 3.16.1
- SQLite
- Aiogram 3.22 (Telegram Bot)
- HTML5, CSS3, JavaScript

## Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/GiornoGiovanaJoJo/hair_purchase_site.git
cd hair_purchase_site
```

### 2. Создание виртуального окружения

```bash
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

### 3. Установка зависимостей

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Настройка окружения

```bash
cp .env.example .env
# Отредактируйте .env файл, добавьте необходимые параметры
```

### 5. Миграции базы данных

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Создание суперпользователя

```bash
python manage.py createsuperuser
```

### 7. Сбор статических файлов

```bash
python manage.py collectstatic --noinput
```

### 8. Запуск сервера разработки

```bash
python manage.py runserver
```

Сайт будет доступен по адресу: http://127.0.0.1:8000/

---

## Файловая структура (ключевое)

```
hair_purchase_site/
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/
│       └── hero.jpg (вы можете заменить на своё)
```

---

## Как заменить изображение в баннере?
Положите своё изображение `hero.jpg` в `static/images/` — оно сразу появится на сайте.

Если файла нет, появится SVG-заглушка.

---

## Решение проблем

### Ошибка 403 CSRF Failed

**Причина:** Django требует CSRF-токен для защиты от атак.

**Решение:**
1. Обновите код из репозитория:
```bash
git pull
```

2. Пересоберите статику:
```bash
python manage.py collectstatic --noinput
```

3. Перезапустите сервер:
```bash
python manage.py runserver
```

4. Обновите страницу в браузере (Ctrl+F5)

### Ошибка 404 на static/images/hero.jpg

**Причина:** Отсутствует файл изображения.

**Решение:**
1. Создайте папку:
```bash
mkdir -p static/images
```

2. Положите любое изображение и назовите `hero.jpg`

3. Пересоберите статику:
```bash
python manage.py collectstatic --noinput
```

4. Обновите страницу в браузере (Ctrl+F5)

**Примечание:** Если файла нет, автоматически появится SVG-заглушка с текстом.

### Калькулятор не работает

1. Откройте DevTools (клавиша F12)
2. Перейдите на вкладку Network
3. Попробуйте рассчитать стоимость
4. Проверьте, что запрос к `/api/calculator/` вернул 200 OK

Если видите 403 — смотрите решение выше.

---

## Развертывание на продакшене

### Важные пункты:

1. **Отключите DEBUG:**
```python
# config/settings.py
DEBUG = False
ALLOWED_HOSTS = ['ваш-домен.ru', 'www.ваш-домен.ru']
```

2. **Используйте надежный SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Копируйте результат в .env

3. **Настройте статику:**
```bash
python manage.py collectstatic --noinput
```

4. **Используйте Gunicorn или uWSGI вместо runserver:**
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

5. **Настройте Nginx для раздачи статики**

---

API и админ-панель действуют по-прежнему. Telegram-бот и backend не затрагивались.

Все вопросы — в Issues или Telegram.