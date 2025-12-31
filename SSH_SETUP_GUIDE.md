# 🔐 ПОШАГОВАЯ ИНСТРУКЦИЯ SSH От GitHub НА Jino VPS

## 🔏 ПРОБЛЕМА (Diagnosis):

Настоящие времени GitHub Actions пытается pull репо SSH:

```bash
# Git remote си (SSH):
git clone git@github.com:GiornoGiovanaJoJo/hair_purchase_site.git

# Но не имеет SSH ключ -> ОШИБКА:
error: could not read Username for 'https://github.com': No such device or address
```

---

## \u2705 РЕШЕНИЕ:

### ШАГ 1: SSH ключ на Jino VPS

Вы работаете по SSH с Jino - значит, используете private SSH ключ для сохранения.

На Jino уже это ключ в `~/.ssh/authorized_keys`.

```bash
ls -la ~/.ssh/
# Ожидается:
# -rw------- authorized_keys
```

### ШАГ 2: НОВЫЙ SSH ключ для Git

Чтобы От GitHub мог ротовать, создаяте новый SSH ключ:

```bash
# SSH рот материал:
ssh-keygen -t ed25519 -f ~/.ssh/github_key -N ""

# Проверить:
ls -la ~/.ssh/github_key*

# Ожидается:
# -rw------- github_key       (приват)
# -rw-r--r-- github_key.pub   (открытый)
```

### ШАГ 3: На GitHub иди ОПУБЛикованно Deploy Key

```bash
# Скопируете открытый ключ:
cat ~/.ssh/github_key.pub
```

**Го в GitHub.com:**
1. Перейте на отнорения: https://github.com/GiornoGiovanaJoJo/hair_purchase_site/settings/keys
2. **Нажмите "Add deploy key"**
3. **Title:** `Jino VPS Deployment Key`
4. **Key:** (пасте открытый контент github_key.pub)
5. **Галочка** "Allow write access" (если что-то требует pull)
6. **Нажмите "Add key"**

### ШАГ 4: Конфигурируете Git на Jino

```bash
# Указать SSH ключ для git:
git config --global core.sshCommand "ssh -i ~/.ssh/github_key -o StrictHostKeyChecking=no"

# Проверить:
git config --global core.sshCommand
# Ожидается: ssh -i ~/.ssh/github_key -o StrictHostKeyChecking=no
```

### ШАГ 5: Правильный URL (SSH)

```bash
# Перекодируете git remote на SSH:
cd /opt/hair_purchase_site
git remote set-url origin git@github.com:GiornoGiovanaJoJo/hair_purchase_site.git

# Проверить:
git remote -v
# Ожидается:
# origin  git@github.com:GiornoGiovanaJoJo/hair_purchase_site.git (fetch)
# origin  git@github.com:GiornoGiovanaJoJo/hair_purchase_site.git (push)
```

### ШАГ 6: ТЕСТИРОВАНИЕ

```bash
# Попытка SSH к GitHub:
ssh -i ~/.ssh/github_key -o StrictHostKeyChecking=no git@github.com
# Ожидается: GitHub does not provide shell access
# (что хорошо Означает)

CTRL+C # Орвить

# Попытка фетча репо:
git fetch origin main
# Ожидается: без ошибок
```

### ШАГ 7: Проверить в GitHub Actions

**После конфига GitHub Actions экономично пытается репо:**

```bash
# Народно бежит деревя pull:
git pull origin main
# Ожидается:
# Already up to date (в тем случае, но влага)
# fast-forward (исли есть новые коммиты)
```

---

## 📋 ЧЕК ТУДА ДЕНЕгс

Пюти, от GitHub пушется:

1. ✅ GitHub Actions триггерется при `git push main`
2. ✅ Тесты работают (если проваляются - проверьте логи)
3. ✅ SSH деплой в Jino: `appleboy/ssh-action`
4. ✅ На сервере бежит:
   - git fetch origin main
   - git reset --hard origin/main
   - python manage.py migrate
   - python manage.py collectstatic
   - sudo systemctl restart hair_purchase

---

## 🪠 ОШИБКа ОПНАвления

Если попражнему один поднавитает:

```bash
error: could not read Username for 'https://github.com': No such device or address
```

Отисочная НАдставка:

```bash
# О Проверюте git remote:
git remote -v

# Если он что-то ещё HTTPS:
git remote set-url origin git@github.com:GiornoGiovanaJoJo/hair_purchase_site.git

# Привендите SSH ключ:
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/github_key

# Тест:
ssh -T git@github.com
# Ожидается: Hi GiornoGiovanaJoJo! You've successfully authenticated, but GitHub does not provide shell access.
```

---

## 🚀 НОВАя ПОЛитика Workflow

**Commit:** `e6d3e3e3604cf311bf566e12251ce4a39cd77c2f`

```yaml
# Теперь столько workflow автоматически работает без HTTPS credentials!
script: |
  git reset --hard origin/main
  git pull origin main
  # Остальное отоо работает автоматически...
```

**Отнесён до автоматически проверяв работа автоматических автоматических автоматический НА ПОНЕДЕЛяНде
