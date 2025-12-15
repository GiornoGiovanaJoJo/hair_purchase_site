# Инструкции по развертыванию исправлений

## РБЛИЧКО

У вас были **500 ошибки** в API калькулятора. **Мы исправили** эти самые ошибки.

Проблема была в неправильной обработке диапазонов длины выходных ("также "40-50", "50-60" итд)

---

## 3 шага для регеерации исправлений

### ШАГ 1️⃣: SSH НА СЕРВЕР

```bash
# Подключитесь к вашему VPS
ssh root@4895c9d9450e.vps.myjino.ru  # Меняйте IP на ваш

# или если используете user
ssh user@4895c9d9450e.vps.myjino.ru
```

### ШАГ 2️⃣: ОБНОВИТЕ КОД

```bash
# Пойте в директорию проекта
cd /path/to/hair_purchase_site

# Если вы не знаете пать, иските:
find / -name "hair_purchase_site" -type d 2>/dev/null
# или
ps aux | grep gunicorn  # Посмотрите куда запускается gunicorn

# Обновить код
git pull origin main
```

### ШАГ 3️⃣: ПЕРЕЗАГРУЖИТЕ DJANGO

**ОПЦИОН А:** Если используете systemd:

```bash
sudo systemctl restart hair-purchase
# или если служба с другим именем:
sudo systemctl restart django_hair_site
```

**ОПЦИОН Б:** Если используете gunicorn ручно:

```bash
# Остановить старый gunicorn
pkill -f gunicorn

# Отдохнить
sleep 2

# Активировать виртуальное окружение
source venv/bin/activate

# Запустить гуникорн
cd /path/to/hair_purchase_site
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 &
```

---

## ПРОВЕРКА ЧТО ВСЕ РАБОТАЕТ

### НА СЕРВЕРЕ:

```bash
# Проверьте логи
journalctl -u hair-purchase -f

# Надо видеть строки вроде:
# ... Application startup complete
# ... Uvicorn running on ...

# Проверьте, что Приложение принимает соединения
curl http://localhost:8000/  # Должна стать ОК (200)
```

### В БРАУЗЕРЕ:

1. **Откройте** https://4895c9d9450e.vps.myjino.ru/

2. **Очистите кеш** (ОЧЕНЬ ВАЖНО!):
   - Windows: `Ctrl + Shift + Delete`
   - Mac: `Cmd + Shift + Delete`
   - Firefox: `Ctrl + Shift + Delete`
   - Edge/Chrome: `Ctrl + Shift + Delete`
   - Выберите "Cookies and cached files"
   - Выберите "All time"
   - Нажмите "Clear"

3. **Обновите** страницу (F5 или Cmd+R)

4. **Перейдите** на закладку "Калькулятор"

5. **Выберите** все параметры:
   - **Длина**: 40-50, 50-60, 60-80, 80-100 или 100+
   - **Цвет**: Любое
   - **Структура**: Любая
   - **Возраст**: Любой
   - **Состояние**: Любое

6. **НАЖМИТЕ** "Рассчитать стоимость"

7. **ПОЛУЧиТЕ** цену (без 500 ошибки! ✓)

---

## Если ОШИБКИ ВСЕ ЕЩЕ ПОЯВЛЯЮТСЯ

### 1. ПРОВЕРЬТЕ ЛОГИ:

```bash
# Джанго логи
journalctl -u hair-purchase -n 100 --output=cat

# или
tail -f /var/log/hair_purchase.log

# Поиск ошибок:
journalctl -u hair-purchase | grep -i "error\|exception\|traceback"
```

### 2. ОТКРОЙТЕ DEVTOOLS В БРАУЗЕРЕ (F12):

- Перейдите на вкладку "Console"
- Попытайтесь рассчитать цену
- Посмотрите в Console на ошибки JavaScript
- Перейдите на вкладку "Network"
- Найдите запрос к `/api/calculator/`
- Правого клик → "Ответы" → Посмотрите фулл JSON

### 3. ПОПЫТАЙТЕСЬ В ШЕЛЛЕ:

```bash
python manage.py shell

from hair_app.price_calculator import calculate_hair_price

# Тест
result = calculate_hair_price(60, 'блонд', 'славянка')
print(f"Price for 60cm blonde slavyanka: {result}")
# Должно вывести: 35000
```

---

## ЧК ДО CHECKLIST

- [ ] Обновил код (`git pull origin main`)
- [ ] Перезагружил Django
- [ ] Очистил кеш браузера
- [ ] Обновил страницу (F5)
- [ ] Попытался рассчитать цену
- [ ] Цена отображается без ошибок (✓)

---

## ФАЙЛЫ, КОТОРЫЕ БЫЛИ ИЗМЕНЕНЫ

✅ `hair_app/views.py` - Основная фикс  
✅ `hair_app/price_calculator.py` - Улучшенная обработка ошибок  
✅ `FIXES_2025_12_15.md` - Подробная документация  

---

## КОГМИТЫ

```
be32a9e4 - fix: improve error handling and length parsing in calculate_price API endpoint
35dbbfe1 - fix: improve error handling in price_calculator for better exception handling
5e58cdda - docs: add detailed fix documentation for API 500 error fixes
```

---

## ПОРОР ЦЕЛЕВЫХ НОМЕрОв

Если вопросы - откройте Issue на GitHub:
https://github.com/GiornoGiovanaJoJo/hair_purchase_site/issues

---

**Ласт упдейт**: 15 Dec 2025  
**Версия**: v1.0 (исправления 500 errors)
