#!/bin/bash

################################################################################
# Hair Purchase Site - Complete Deployment Script
# Jino VPS Ubuntu 24.04 LTS
# Использование: bash scripts/deploy.sh
################################################################################

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции
print_header() {
    echo -e "${BLUE}\n========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Проверка, запущен ли скрипт от root
if [[ $EUID -ne 0 ]]; then
    print_error "Этот скрипт должен запускаться от root!"
    echo "Используйте: sudo bash scripts/deploy.sh"
    exit 1
fi

# Переменные
PROJECT_PATH="/opt/hair_purchase_site"
VENV_PATH="${PROJECT_PATH}/venv"
PYTHON_VERSION="3.11"
NGINX_CONF_PATH="/etc/nginx/sites-available"
SYSTEMD_PATH="/etc/systemd/system"

print_header "Hair Purchase Site - Полная установка"

# ============================================================================
# Шаг 1: Обновление системы
# ============================================================================
print_header "Шаг 1: Обновление системы"

apt-get update
apt-get upgrade -y
apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-venv \
    python${PYTHON_VERSION}-dev \
    python3-pip \
    nginx \
    git \
    curl \
    wget \
    postgresql \
    postgresql-contrib \
    redis-server \
    certbot \
    python3-certbot-nginx \
    supervisor \
    htop \
    vim \
    tmux

print_success "Система обновлена"

# ============================================================================
# Шаг 2: Подготовка директорий
# ============================================================================
print_header "Шаг 2: Подготовка директорий"

mkdir -p ${PROJECT_PATH}
mkdir -p /var/log/hair_purchase
mkdir -p /var/run/hair_purchase

print_success "Директории созданы"

# ============================================================================
# Шаг 3: Git клонирование (если нужно)
# ============================================================================
print_header "Шаг 3: Клонирование репозитория"

if [ ! -d "${PROJECT_PATH}/.git" ]; then
    cd /opt
    git clone https://github.com/GiornoGiovanaJoJo/hair_purchase_site.git
    print_success "Репозиторий клонирован"
else
    cd ${PROJECT_PATH}
    git pull origin main
    print_success "Репозиторий обновлен"
fi

# ============================================================================
# Шаг 4: Настройка виртуального окружения
# ============================================================================
print_header "Шаг 4: Настройка Python виртуального окружения"

cd ${PROJECT_PATH}
python${PYTHON_VERSION} -m venv ${VENV_PATH}
source ${VENV_PATH}/bin/activate

pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

print_success "Виртуальное окружение создано"

# ============================================================================
# Шаг 5: Настройка БД (PostgreSQL)
# ============================================================================
print_header "Шаг 5: Настройка базы данных"

# Запуск PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Создание пользователя и БД
sudo -u postgres psql << EOF || print_warning "БД может быть уже создана"
CREATE USER hair_user WITH PASSWORD 'hair_secure_password';
ALTER ROLE hair_user SET client_encoding TO 'utf8';
ALTER ROLE hair_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE hair_user SET default_transaction_deferrable TO on;
ALTER ROLE hair_user SET timezone TO 'UTC';
CREATE DATABASE hair_db OWNER hair_user;
EOF

print_success "База данных настроена"

# ============================================================================
# Шаг 6: Настройка Django
# ============================================================================
print_header "Шаг 6: Настройка Django приложения"

cd ${PROJECT_PATH}

# Создание .env файла
cat > .env << 'EOF'
DEBUG=False
SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
ALLOWED_HOSTS=your_domain.com,www.your_domain.com,4895c9d9450e.vps.myjino.ru,localhost,127.0.0.1
DATABASE_URL=postgresql://hair_user:hair_secure_password@localhost:5432/hair_db
STATIC_URL=/static/
MEDIA_URL=/media/
TELEGRAM_BOT_TOKEN=your_telegram_token
TELEGRAM_ADMIN_CHAT_ID=your_admin_chat_id
TELEGRAM_USE_WEBHOOK=False
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CSRF_TRUSTED_ORIGINS=https://your_domain.com,https://www.your_domain.com
EOF

print_warning "ВАЖНО: Отредактируйте .env файл с правильными значениями!"
print_warning "nano .env"

# Активация виртуального окружения и миграция БД
source ${VENV_PATH}/bin/activate

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser --noinput --username admin --email admin@example.com || print_warning "Суперпользователь может быть уже создан"

print_success "Django приложение настроено"

# ============================================================================
# Шаг 7: Настройка Gunicorn systemd сервис
# ============================================================================
print_header "Шаг 7: Настройка Gunicorn сервиса"

cat > ${SYSTEMD_PATH}/hair_purchase.service << EOF
[Unit]
Description=Hair Purchase Django Application
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=notify
User=root
Group=www-data
WorkingDirectory=${PROJECT_PATH}
Environment="PATH=${VENV_PATH}/bin"
ExecStart=${VENV_PATH}/bin/gunicorn \\
    config.wsgi:application \\
    --bind 0.0.0.0:8000 \\
    --workers 3 \\
    --worker-class sync \\
    --timeout 60 \\
    --access-logfile /var/log/hair_purchase/access.log \\
    --error-logfile /var/log/hair_purchase/error.log

ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
KillSignal=SIGQUIT
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

print_success "Gunicorn сервис создан"

# ============================================================================
# Шаг 8: Настройка Telegram Bot сервис
# ============================================================================
print_header "Шаг 8: Настройка Telegram Bot сервиса"

cat > ${SYSTEMD_PATH}/hair_purchase_bot.service << EOF
[Unit]
Description=Hair Purchase Telegram Bot
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=${PROJECT_PATH}
Environment="PATH=${VENV_PATH}/bin"
ExecStart=${VENV_PATH}/bin/python telegram_bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

print_success "Telegram Bot сервис создан"

# ============================================================================
# Шаг 9: Настройка Nginx
# ============================================================================
print_header "Шаг 9: Настройка Nginx"

cat > ${NGINX_CONF_PATH}/hair_purchase << 'EOF'
upstream gunicorn {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    listen [::]:80;
    server_name _;
    client_max_body_size 100M;

    # Логи
    access_log /var/log/nginx/hair_purchase_access.log;
    error_log /var/log/nginx/hair_purchase_error.log;

    location / {
        proxy_pass http://gunicorn;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
    }

    location /static/ {
        alias /opt/hair_purchase_site/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /opt/hair_purchase_site/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Health check endpoint
    location /health {
        proxy_pass http://gunicorn;
        access_log off;
    }
}
EOF

# Активация конфига Nginx
ln -sf ${NGINX_CONF_PATH}/hair_purchase /etc/nginx/sites-enabled/hair_purchase 2>/dev/null || true
rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true

# Проверка конфига и перезагрузка
nginx -t && systemctl restart nginx

print_success "Nginx настроен"

# ============================================================================
# Шаг 10: Включение и запуск сервисов
# ============================================================================
print_header "Шаг 10: Запуск сервисов"

systemctl daemon-reload
systemctl enable hair_purchase.service
systemctl enable hair_purchase_bot.service
systemctl start hair_purchase.service
systemctl start hair_purchase_bot.service

print_success "Сервисы запущены"

# ============================================================================
# Шаг 11: SSL сертификат (Let's Encrypt)
# ============================================================================
print_header "Шаг 11: Настройка SSL сертификата"

echo "Для настройки SSL сертификата выполните:"
echo "sudo certbot --nginx -d your_domain.com -d www.your_domain.com"
echo ""

# ============================================================================
# Шаг 12: Логирование и мониторинг
# ============================================================================
print_header "Шаг 12: Настройка логирования"

# Создание логов
touch /var/log/hair_purchase/access.log
touch /var/log/hair_purchase/error.log
chown root:www-data /var/log/hair_purchase
chmod 750 /var/log/hair_purchase

print_success "Логирование настроено"

# ============================================================================
# Финальная проверка
# ============================================================================
print_header "Финальная проверка"

echo "Статус сервисов:"
systemctl status hair_purchase.service --no-pager || print_error "Ошибка при запуске hair_purchase"
systemctl status hair_purchase_bot.service --no-pager || print_error "Ошибка при запуске hair_purchase_bot"

echo ""
echo "Проверка портов:"
netstat -tlnp 2>/dev/null | grep -E "8000|80|443" || echo "Порты еще не слушают"

echo ""
echo "Проверка логов:"
tail -10 /var/log/hair_purchase/error.log

# ============================================================================
# Итоговая информация
# ============================================================================
print_header "✅ Установка завершена!"

echo "Полезные команды:"
echo ""
echo "📋 Статус сервиса:"
echo "  sudo systemctl status hair_purchase"
echo ""
echo "🔄 Перезагрузка:"
echo "  sudo systemctl restart hair_purchase"
echo "  sudo systemctl restart nginx"
echo ""
echo "📝 Просмотр логов:"
echo "  tail -f /var/log/hair_purchase/error.log"
echo "  tail -f /var/log/nginx/hair_purchase_access.log"
echo ""
echo "🛡️  Установка SSL:"
echo "  sudo certbot --nginx"
echo ""
echo "📊 Администратор Django:"
echo "  cd ${PROJECT_PATH}"
echo "  source ${VENV_PATH}/bin/activate"
echo "  python manage.py createsuperuser"
echo ""
echo "🌐 Приложение доступно на: http://your_domain.com"
echo ""

print_success "Спасибо за использование скрипта!"
