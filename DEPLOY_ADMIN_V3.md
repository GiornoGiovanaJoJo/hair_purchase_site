# Deploy Custom Admin v3 На Продакшн

## На Чю Готово?

Ниже готовые команды для быстрого деплоя. Копируйте и вставляйте команды одну за другой!

---

## ШАГ 1: Принести исправления

```bash
ssh -p 49196 root@4895c9d9450e.vps.myjino.ru
cd /opt/hair_purchase_site
git pull origin main
```

**Ожидаемые файлы:**
```
✅ hair_app/admin_views.py (NEW)
✅ hair_app/admin_utils.py (NEW)
✅ hair_app/admin_views_export.py (NEW)
✅ hair_app/templates/admin/custom_dashboard.html (NEW)
✅ hair_app/admin.py (UPDATED)
✅ config/urls.py (UPDATED)
✅ requirements.txt (UPDATED)
```

---

## ШАГ 2: Установить зависимости

```bash
pip install -r requirements.txt
```

или быстро:

```bash
pip install openpyxl
```

---

## ШАГ 3: Миграции

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

---

## ШАГ 4: Перезагрузить Django

```bash
sudo systemctl restart hair_purchase
```

---

## ШАГ 5: ПРОВЕРКА!

### 5.1 Проверить Логи

```bash
journalctl -u hair_purchase -n 30 --no-pager
```

Ожидаемые логи:
```
Dec 16 19:45:00 ... gunicorn[...]: Starting gunicorn ...
Dec 16 19:45:02 ... gunicorn[...]: Application startup complete
👋 Нет ошибок!
```

### 5.2 Тестировать админку

```bash
curl -I http://4895c9d9450e.vps.myjino.ru/admin/
```

Ожидаемые ответы:
```
HTTP/1.1 301 Moved Permanently  (залогинен или ждёт login)
HTTP/1.1 200 OK                 (уже в админке)
NOT 500 Internal Server Error!  ✅
```

### 5.3 Открыть в браузере

```
https://4895c9d9450e.vps.myjino.ru/admin/
```

Ожидаемые элементы:
- ✅ Красивые статистические карточки
- ✅ График с данными
- ✅ Список последних заявок
- ✅ Кнопки экспорта (CSV, Excel)

### 5.4 Тест Экспорта

Открыть в браузере:

```
https://4895c9d9450e.vps.myjino.ru/admin/export/applications/csv/
```

Ожидаемые резултаты:
- ✅ Начнётся загружка CSV файла
- ✅ Название: `applications.csv`

```
https://4895c9d9450e.vps.myjino.ru/admin/export/applications/excel/
```

Ожидаемые резултаты:
- ✅ Начнётся загружка Excel файла
- ✅ Название: `applications.xlsx`
- ✅ Файл раскрывается в Excel с красивым форматированием

---

## ПОЛНАЯ Ордина команд (Копируйте все сразу)

```bash
# Подключитесь с SSH
ssh -p 49196 root@4895c9d9450e.vps.myjino.ru

# Навигация
cd /opt/hair_purchase_site

# Обновление кода
git pull origin main

# Очистка кэша
rm -rf ~/.cache/pip

# Установка зависимостей
pip install -r requirements.txt --upgrade

# Миграции базы
python manage.py migrate

# Обновление статических файлов
python manage.py collectstatic --noinput

# Перезагружка сервиса
sudo systemctl restart hair_purchase

# Проверка логов
journalctl -u hair_purchase -n 30 --no-pager

# Проверка статуса сервера
curl -I http://4895c9d9450e.vps.myjino.ru/admin/
```

---

## Отваливание (Если Что-то Ошибка)

### Ошибка 500

```bash
# Посмотреть опасные логи
journalctl -u hair_purchase -n 100 --no-pager | grep -i error

# Перестарт gunicorn
sudo systemctl restart hair_purchase
```

### Ошибка "Template not found"

```bash
# Проверить файлы
ls -la /opt/hair_purchase_site/hair_app/templates/admin/

# Если не есть:
git status
git pull origin main
```

### Ошибка "No module named 'openpyxl'"

```bash
pip install openpyxl==3.10.0

# Навернок:
pip list | grep openpyxl

# Перестартите:
sudo systemctl restart hair_purchase
```

### Ошибка При Гите

```bash
# Посмотреть новые файлы
git status

# Если изменения:
git fetch origin main
git reset --hard origin/main
git pull origin main
```

---

## МОНИТОРИНГ ПОсле Деплоя

### Проверить жив ли сервис

```bash
# Проверить статус
sudo systemctl status hair_purchase

# Если не работает:
sudo systemctl start hair_purchase
sudo systemctl restart hair_purchase
```

### Нанесение нагрузки

```bash
# Посмотреть топ процессов
top -b -n 1 | grep python

# Монитор CPU и RAM
watch -n 1 'free -h && echo && ps aux | grep python'
```

### Проверить диск

```bash
df -h
du -sh /opt/hair_purchase_site/
```

---

## Критические Команды

### Откат КОДА (Если Что-то идет НЕ ВО НАжать CTRL+C)

```bash
# Найти историю git
git log --oneline | head -5

# Откат на предыдущий коммит (ID взять из млоги свыше)
git reset --hard <COMMIT_ID>

# Откат на main
git reset --hard origin/main

# Перестарт сервиса
sudo systemctl restart hair_purchase
```

---

## ПОСЛЕ НОРМАЛЬНОГО ДЕПЛОЯ

Проверить чеклист:

- ✅ Панель управления доступна по https://4895c9d9450e.vps.myjino.ru/admin/
- ✅ График отображает антные данные
- ✅ Статистика поновляется
- ✅ Экспорт CSV работает
- ✅ Экспорт Excel работает
- ✅ Таблицы с хорошим дизайном
- ✅ Мастер акции (принять/отклонить/завершить) работают
- ✅ Логи нормальные (journalctl -u hair_purchase -n 20 --no-pager)

**ОТЛИЧНО! Админка v3 работает! ✅**

---

## Файлы для справки

- [ADMIN_SETUP.md](./ADMIN_SETUP.md) - Полная документация
- [hair_app/admin_views.py](./hair_app/admin_views.py) - Новые views
- [hair_app/admin_utils.py](./hair_app/admin_utils.py) - Экспорт утилиты
- [hair_app/admin_views_export.py](./hair_app/admin_views_export.py) - Экспорт views

---

**Написано:** 16 декабря 2025  
**Версия:** v3.0.0  
**Статус:** Production Ready 🚀
