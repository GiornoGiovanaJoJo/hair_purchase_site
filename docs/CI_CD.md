# CI/CD Настройка

Этот документ описывает настройку CI/CD для проекта Hair Purchase Site.

## 📦 Что включено

- **GitHub Actions** - автоматическое тестирование
- **Docker** - контейнеризация приложения
- **Docker Compose** - оркестрация сервисов
- **Nginx** - reverse proxy и раздача статики
- **Automated Deployment** - автоматический деплой на сервер

---

## 🚀 GitHub Actions Workflow

### Что происходит при каждом push:

1. **Test Job** - тестирование кода
   - Проверка линтером (flake8)
   - Запуск миграций
   - Запуск тестов
   - Генерация coverage отчета

2. **Build Job** - сборка Docker образа
   - Сборка Docker образа
   - Опционально: отправка в Docker Hub

3. **Deploy Job** - деплой на сервер
   - SSH подключение к серверу
   - Обновление кода
   - Перезапуск сервисов

---

## ⚙️ Настройка GitHub Secrets

Для работы CI/CD нужно добавить secrets в GitHub репозиторий:

### Как добавить secrets:

1. Перейдите в репозиторий на GitHub
2. Settings → Secrets and variables → Actions
3. New repository secret

### Необходимые secrets:

#### **Для деплоя на сервер:**

```
DEPLOY_HOST          # IP адрес вашего сервера (например: 192.168.1.100)
DEPLOY_USER          # Имя пользователя SSH (например: root)
DEPLOY_SSH_KEY       # Приватный SSH ключ для подключения
DEPLOY_PORT          # Порт SSH (опционально, по умолчанию: 22)
```

#### **Для Docker Hub (опционально):**

```
DOCKER_USERNAME      # Ваш username на Docker Hub
DOCKER_PASSWORD      # Ваш password или access token Docker Hub
```

---

## 📦 Сгенерировать SSH ключ

Если у вас нет SSH ключа:

```bash
# 1. Сгенерировать новый ключ
ssh-keygen -t ed25519 -C "github-actions@hair-site"

# 2. Добавить публичный ключ на сервер
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@your-server-ip

# 3. Скопировать приватный ключ
cat ~/.ssh/id_ed25519

# 4. Добавить его в GitHub Secrets как DEPLOY_SSH_KEY
```

---

## 🐳 Локальный запуск с Docker

### Первый запуск:

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/GiornoGiovanaJoJo/hair_purchase_site.git
cd hair_purchase_site

# 2. Создайте .env файл
cp .env.example .env
# Отредактируйте .env файл со своими значениями

# 3. Соберите и запустите контейнеры
docker-compose up -d --build

# 4. Примените миграции
docker-compose exec web python manage.py migrate

# 5. Создайте суперпользователя
docker-compose exec web python manage.py createsuperuser

# 6. Соберите статику
docker-compose exec web python manage.py collectstatic --noinput
```

### Полезные команды:

```bash
# Просмотр логов
docker-compose logs -f web      # логи Django
docker-compose logs -f bot      # логи Telegram бота
docker-compose logs -f db       # логи базы данных

# Статус контейнеров
docker-compose ps

# Перезапуск сервиса
docker-compose restart web
docker-compose restart bot

# Остановка всех сервисов
docker-compose down

# Полная очистка (удаление volumes)
docker-compose down -v
```

---

## 🖥️ Деплой на продакшн сервер

### Подготовка сервера:

```bash
# 1. Установите Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 2. Установите Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. Клонируйте репозиторий
cd /opt
sudo git clone https://github.com/GiornoGiovanaJoJo/hair_purchase_site.git
cd hair_purchase_site

# 4. Создайте .env файл
sudo nano .env
# Добавьте все необходимые переменные

# 5. Запустите скрипт деплоя
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### Автоматический деплой:

После настройки GitHub Secrets, каждый push в `main` будет автоматически:

1. Тестировать код
2. Собирать Docker образ
3. Подключаться к серверу по SSH
4. Обновлять код
5. Перезапускать сервисы

---

## 🔒 Настройка SSL (опционально)

Используйте Let's Encrypt для бесплатного SSL сертификата:

```bash
# 1. Установите certbot
sudo apt-get install certbot python3-certbot-nginx

# 2. Получите сертификат
sudo certbot --nginx -d your-domain.com

# 3. Раскомментируйте HTTPS блок в nginx/conf.d/hair_site.conf
# 4. Перезапустите nginx
docker-compose restart nginx
```

---

## 📊 Мониторинг

### Проверка статуса сервисов:

```bash
# Проверка здоровья сервисов
docker-compose ps

# Проверка доступности сайта
curl http://localhost

# Проверка базы данных
docker-compose exec db psql -U hair_user -d hair_db -c "SELECT 1;"
```

### Статус GitHub Actions:

Перейдите в репозиторий на GitHub → Actions

---

## 🐛 Решение проблем

### CI/CD не запускается:

1. Проверьте GitHub Secrets
2. Убедитесь, что workflow файл существует: `.github/workflows/django-ci.yml`

### Docker контейнеры не запускаются:

```bash
# Проверьте логи
docker-compose logs

# Пересоберите образы
docker-compose build --no-cache

# Полная перезагрузка
docker-compose down -v
docker-compose up -d --build
```

### Проблемы с деплоем:

1. Проверьте SSH ключ
2. Убедитесь, что сервер доступен
3. Проверьте права доступа к папке `/opt/hair_purchase_site`

---

## 📚 Дополнительные ресурсы

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Nginx Configuration](https://nginx.org/en/docs/)

---

## 🚀 Следующие шаги

1. ✅ Настройте GitHub Secrets
2. ✅ Проверьте локальный запуск с Docker
3. ✅ Подготовьте продакшн сервер
4. ✅ Сделайте push в main и проверьте деплой
5. ✅ Настройте SSL сертификат
