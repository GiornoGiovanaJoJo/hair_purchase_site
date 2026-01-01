# 🚀 GitHub Actions CI/CD и Deploy на Jino VPS

## 💬 Оптимальные настройки для вашего проекта

**Проект:** Hair Purchase Site  
**Framework:** Django 5.2 LTS  
**Server:** Jino VPS (Ubuntu 24.04)  
**Python:** 3.11 / 3.12  
**DB:** PostgreSQL 15  
**Web Server:** Nginx + Gunicorn  

---

## 📜 Структура GitHub Actions Pipeline

### Stage 1: 🧪 Тестирование и проверка качества (15 мин)
- ✅ Проверка синтаксиса (Flake8)
- ✅ Форматирование кода (Black, isort)
- ✅ Проверка безопасности (Safety)
- ✅ Миграции БД
- ✅ Django system checks
- ✅ Unit тесты (pytest)
- ✅ Code coverage отчет

### Stage 2: 🐳 Build Docker Image (опционально)
- ✅ Сборка Docker образа
- ✅ Push на GitHub Container Registry

### Stage 3: 🚀 Deploy на VPS
- ✅ SSH подключение к серверу
- ✅ Git pull
- ✅ Установка зависимостей
- ✅ Миграции БД
- ✅ Сбор статики
- ✅ Перезагрузка сервисов

### Stage 4: 📧 Уведомления
- ✅ Успешный deploy
- ✅ Ошибки в pipeline

---

## 🔑 Требуемые GitHub Secrets

Перейдите в: **Settings → Secrets and variables → Actions**

Добавьте следующие secrets:

### 1. VPS подключение

```
VPS_HOST = 195.161.69.221
VPS_USER = root
VPS_SSH_KEY = (ваш приватный SSH ключ)
VPS_PROJECT_PATH = /opt/hair_purchase_site
```

### 2. Как получить SSH ключ

**Если у вас уже есть ключ:**
```bash
cat ~/.ssh/id_rsa
# Скопируйте весь вывод (включая -----BEGIN...-----END-----)
```

**Если нет ключа, сгенерируйте:**
```bash
# На вашем компьютере
ssh-keygen -t rsa -b 4096 -f ~/.ssh/jino_deploy -N ""

# Скопируйте приватный ключ
cat ~/.ssh/jino_deploy

# Добавьте публичный на VPS
ssh-copy-id -i ~/.ssh/jino_deploy.pub root@195.161.69.221
# или
cat ~/.ssh/jino_deploy.pub | ssh root@195.161.69.221 "cat >> ~/.ssh/authorized_keys"
```

### 3. Добавление в GitHub

1. Откройте GitHub репозиторий
2. **Settings → Secrets and variables → Actions**
3. **New repository secret**
4. Добавьте каждый secret:

```
Name: VPS_HOST
Secret: 195.161.69.221

Name: VPS_USER
Secret: root

Name: VPS_SSH_KEY
Secret: (весь текст приватного ключа с BEGIN и END)

Name: VPS_PROJECT_PATH
Secret: /opt/hair_purchase_site
```

---

## 📋 Подготовка VPS к автоматическому deploy

### Шаг 1: Запустите скрипт развертывания

```bash
# На VPS от root
sudo bash scripts/deploy.sh
```

Этот скрипт установит:
- ✅ Python 3.11
- ✅ PostgreSQL
- ✅ Redis
- ✅ Nginx
- ✅ Systemd сервисы (hair_purchase, hair_purchase_bot)
- ✅ Все зависимости

### Шаг 2: Проверьте установку

```bash
# Проверьте сервисы
sudo systemctl status hair_purchase
sudo systemctl status hair_purchase_bot

# Проверьте порты
sudo ss -tlnp | grep -E "8000|80"

# Проверьте БД
sudo -u postgres psql -l | grep hair_db
```

### Шаг 3: Отредактируйте .env

```bash
sudo nano /opt/hair_purchase_site/.env
```

Обновите:
```
DEBUG=False
SECRET_KEY=ваш-новый-ключ
ALLOWED_HOSTS=your_domain.com,www.your_domain.com,195.161.69.221
TELEGRAM_BOT_TOKEN=ваш-токен
```

### Шаг 4: Настройте SSL (Let's Encrypt)

```bash
# Если домен уже настроен на сервер
sudo certbot --nginx -d your_domain.com -d www.your_domain.com
```

---

## 🚀 Триггеры и условия

### Когда запускается pipeline

- ✅ **Push в main** → полный pipeline (test + build + deploy)
- ✅ **Push в develop** → только test + build
- ✅ **Pull request** → только test

### Условия deploy

```yaml
if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```

Deploy запускается **только** при push в main ветку!

---

## 📊 Мониторинг pipeline

### Просмотр логов

1. Откройте репозиторий на GitHub
2. **Actions** вкладка
3. Выберите последний run
4. Посмотрите детали каждого job

### Типичные проблемы

**❌ SSH ключ не работает**
```bash
# На VPS проверьте authorized_keys
cat ~/.ssh/authorized_keys

# Повторно добавьте ключ
echo "ваш-публичный-ключ" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

**❌ Миграции не применяются**
```bash
# На VPS вручную
cd /opt/hair_purchase_site
source venv/bin/activate
python manage.py migrate
```

**❌ Сервис не стартует**
```bash
# Проверьте статус
sudo systemctl status hair_purchase
sudo journalctl -u hair_purchase -n 50

# Перезагрузите
sudo systemctl restart hair_purchase
```

---

## 🔒 Безопасность

### Лучшие практики

1. **Никогда** не коммитьте .env
   ```bash
   # .gitignore должен содержать
   .env
   .env.local
   *.pem
   *.key
   ```

2. **SSH ключ** хранится только в GitHub Secrets
   - Не коммитьте в репозиторий
   - Используйте разные ключи для разных серверов
   - Регулярно меняйте ключи

3. **Secrets ротация**
   ```bash
   # Периодически обновляйте SECRET_KEY Django
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

4. **Ограничения доступа**
   - Используйте deploy ключи (deploy keys)
   - Ограничьте доступ к main ветке
   - Требуйте code review перед merge

---

## 📝 Полезные команды

### Локальное тестирование

```bash
# Установите зависимости
pip install -r requirements.txt

# Запустите тесты локально
python -m pytest --verbose

# Проверьте код
flake8 .
black --check .
isort --check-only .

# Запустите Django checks
python manage.py check
python manage.py makemigrations --dry-run --check
```

### На VPS

```bash
# Статус сервисов
sudo systemctl status hair_purchase hair_purchase_bot nginx

# Перезагрузка
sudo systemctl restart hair_purchase
sudo systemctl restart nginx

# Логи
tail -f /var/log/hair_purchase/error.log
tail -f /var/log/nginx/hair_purchase_access.log

# Вход в БД
sudo -u postgres psql hair_db

# Вход в Django shell
cd /opt/hair_purchase_site
source venv/bin/activate
python manage.py shell
```

---

## 🎯 Чек-лист первого deploy

- [ ] SSH ключ добавлен в GitHub Secrets
- [ ] VPS_HOST, VPS_USER, VPS_SSH_KEY, VPS_PROJECT_PATH заполнены
- [ ] Скрипт deploy.sh запущен на VPS
- [ ] PostgreSQL БД создана и настроена
- [ ] .env файл обновлен на VPS
- [ ] Сервисы запущены: `systemctl status hair_purchase`
- [ ] Nginx работает: `curl http://localhost`
- [ ] Push тестовый коммит в main ветку
- [ ] GitHub Actions запустился (Actions вкладка)
- [ ] Deploy прошел успешно
- [ ] Приложение доступно по адресу
- [ ] Проверены логи сервиса

---

## 📞 Troubleshooting

### 1. GitHub Actions не запускается

```yaml
# Проверьте workflow файл
.github/workflows/django-ci.yml

# Убедитесь, что синтаксис YAML правильный
# (используйте https://www.yamllint.com/)
```

### 2. Deploy не срабатывает

```bash
# На VPS проверьте SSH доступ
ssh -v root@195.161.69.221

# Проверьте права на ключ
ls -la ~/.ssh/
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### 3. Миграции падают

```bash
# На VPS
cd /opt/hair_purchase_site
source venv/bin/activate

# Проверьте в какой папке вы находитесь
pwd

# Запустите миграцию вручную
python manage.py migrate --verbosity=2

# Если ошибка в коде миграции
python manage.py showmigrations
python manage.py migrate app_name --zero
```

### 4. Gunicorn не стартует

```bash
# Проверьте статус
sudo journalctl -u hair_purchase -n 100

# Проверьте права доступа
ls -la /opt/hair_purchase_site

# Перезагрузите
sudo systemctl restart hair_purchase
```

---

## 📈 Мониторинг и логирование

### Структура логов

```
/var/log/hair_purchase/
├── access.log      # Gunicorn access лог
└── error.log       # Gunicorn error лог

/var/log/nginx/
├── hair_purchase_access.log
└── hair_purchase_error.log

/var/log/syslog    # Systemd логи
```

### Просмотр логов

```bash
# Последние 50 строк ошибок
tail -50 /var/log/hair_purchase/error.log

# Следить за логами в реальном времени
tail -f /var/log/hair_purchase/error.log

# Искать конкретную ошибку
grep "ошибка" /var/log/hair_purchase/error.log

# Systemd логи
sudo journalctl -u hair_purchase -n 50
sudo journalctl -u hair_purchase -f  # Follow mode
```

---

## ✅ Финальная проверка

После успешного deploy проверьте:

```bash
# 1. Приложение доступно
curl -I http://your_domain.com

# 2. Admin панель работает
curl -I http://your_domain.com/admin/

# 3. API доступен
curl http://your_domain.com/api/

# 4. Статика загружается
curl -I http://your_domain.com/static/...

# 5. Сервис запущен
sudo systemctl status hair_purchase | grep running

# 6. БД подключена
sudo -u postgres psql hair_db -c "SELECT 1;"
```

---

## 📚 Полезные ссылки

- [GitHub Actions документация](https://docs.github.com/en/actions)
- [Django deployment гайд](https://docs.djangoproject.com/en/5.2/howto/deployment/)
- [Gunicorn docs](https://gunicorn.org/)
- [Nginx reverse proxy](https://nginx.org/en/docs/)
- [PostgreSQL документация](https://www.postgresql.org/docs/)
- [Let's Encrypt](https://letsencrypt.org/)

---

**Статус:** ✅ Готово к продакшену  
**Последнее обновление:** 1 января 2026  
**Версия:** 1.0
