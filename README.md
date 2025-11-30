# Hair Purchase Site

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

Админ-панель: http://127.0.0.1:8000/admin/

API документация: http://127.0.0.1:8000/api/docs/

## Telegram бот

### Настройка бота

1. Создайте бота через @BotFather в Telegram
2. Получите токен бота
3. Добавьте токен в `.env` файл:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_MAIN_ADMIN_ID=your_telegram_id
   ```
4. Узнайте свой Telegram ID у @userinfobot

### Запуск бота

```bash
python manage.py run_telegram_bot
```

### Добавление администраторов

1. Откройте админ-панель Django
2. Перейдите в раздел "Telegram администраторы"
3. Добавьте нового администратора, указав его Telegram ID

## Структура проекта

```
hair_purchase_site/
├── config/                 # Настройки проекта
│   ├── settings.py
│   ├── urls.py
│   └── telegram_settings.py
├── hair_app/              # Основное приложение
│   ├── models.py          # Модели данных
│   ├── views.py           # Представления
│   ├── serializers.py     # Сериализаторы DRF
│   ├── admin.py           # Настройки админки
│   └── management/        # Django команды
├── telegram_bot/          # Telegram бот
│   ├── bot.py            # Главный файл бота
│   ├── handlers/         # Обработчики команд
│   ├── keyboards/        # Клавиатуры
│   └── filters/          # Фильтры
├── templates/            # HTML шаблоны
├── static/              # Статические файлы
├── media/               # Загружаемые файлы
├── requirements.txt     # Зависимости
└── manage.py           # Django management
```

## API Endpoints

- `GET /api/applications/` - Список всех заявок
- `POST /api/applications/` - Создать заявку
- `GET /api/applications/{id}/` - Детали заявки
- `POST /api/calculator/` - Рассчитать стоимость
- `GET /api/price-list/` - Прайс-лист

## Переменные окружения

Основные переменные в `.env` файле:

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Яндекс.Метрика
YANDEX_METRIKA_ID=your_metrika_id

# Email
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_password
ADMIN_EMAIL=admin@example.com

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_MAIN_ADMIN_ID=your_telegram_id
```

## Production Deploy

### С использованием Gunicorn

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### С использованием systemd (Linux)

Создайте файл `/etc/systemd/system/hair_purchase.service`:

```ini
[Unit]
Description=Hair Purchase Site
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/hair_purchase_site
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn config.wsgi:application --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start hair_purchase
sudo systemctl enable hair_purchase
```

## Лицензия

MIT License

## Контакты

Для вопросов и предложений: [ваш email]
