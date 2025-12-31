# 🚀 ИСПРАВЛЕНИЕ ОШИБКИ РАЗВЕРТЫВАНИЯ

## ❌ Проблема:

```
error: could not read Username for 'https://github.com': No such device or address
fatal: could not read Username for 'https://github.com': No such device or address
Process exited with status 128
```

**Причина:** Сервер не может аутентифицироваться на GitHub при выполнении `git pull` 

---

## ✅ РЕШЕНИЕ - ВЫБОР #1 (ОтОПравлено)

### Workflow уже обновлен!

**Исправлено** `.github/workflows/django-ci.yml` с добавлением:

```yaml
# Configure git to use HTTPS with token (if available)
echo "Configuring Git credentials..."
if [ -n "$GIT_TOKEN" ]; then
  git config --global credential.helper store
  echo "https://$GIT_USER:$GIT_TOKEN@github.com" > ~/.git-credentials
  chmod 600 ~/.git-credentials
  echo "✅ Git credentials configured"
fi
```

Теперь используется `GITHUB_TOKEN` (доступен автоматически в GitHub Actions)

---

## 📂 РЕШЕНИЕ - ОПЦИОНАЛЬНО

### Вариант 1: SSH ключ на сервере

```bash
# 1. На сервере (в SSH)
cd /opt/hair_purchase_site

# 2. Настроите Git для SSH
git remote set-url origin git@github.com:GiornoGiovanaJoJo/hair_purchase_site.git

# 3. Подготовьте SSH ключ
# Если пользователь deploy:
sudo -u deploy ssh-keygen -t ed25519 -f ~/.ssh/github_key -N ""

# 4. Добавьте ключ в GitHub (Settings -> Deploy keys)
cat ~/.ssh/github_key.pub
# скопируйте вывод в GitHub

# 5. Настроите SSH config
mkdir -p ~/.ssh
cat > ~/.ssh/config << 'EOF'
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/github_key
  StrictHostKeyChecking no
EOF

chmod 600 ~/.ssh/config

# 6. Тестируюте SSH коннекцию
sudo -u deploy ssh -T git@github.com
# Ожидаемая ответ:
# Hi GiornoGiovanaJoJo! You've successfully authenticated, but GitHub does not provide shell access.
```

### Вариант 2: Personal Access Token

```bash
# 1. На GitHub:
#    Settings -> Developer settings -> Personal access tokens -> Fine-grained tokens
#    Содав токен с доступом к репозиторию

# 2. На сервере:
git config --global credential.helper store
echo "https://YOUR_USERNAME:YOUR_TOKEN@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials

# 3. Тестируюте:
cd /opt/hair_purchase_site
git pull origin main
# Не должно быть ошибок
```

---

## 🌟 Одрючаемые альтернативы

### Опция 3: Deploy через GitHub Deployment API

```bash
# 1. Установить всё выше, потом:

# 2. В workflow добавимые:
environment:
  name: production
  url: https://4895c9d9450e.vps.myjino.ru

# 3. Положите secrets для Production:
#    Settings -> Environments -> Production -> Add secret
```

---

## 🔆 БЫСТРЫЙ СТАТУС-ЧЕК

### Проверите текущие секреты:

```bash
# На GitHub Settings -> Secrets and variables -> Actions
# Должны существовать:

✅ DEPLOYHOST       # IP адрес сервера
✅ DEPLOYUSER       # Пользователь SSH (например: root, deploy)
✅ DEPLOYSSHKEY     # Приватный SSH ключ
✅ DEPLOYPORT       # Порт SSH (обычно 22)
```

---

## 🚀 ТЕСТИРОВАНИЕ

### Локально на сервере:

```bash
# 1. Проверите что гит работает
cd /opt/hair_purchase_site
git status

# 2. Попытайтесь pull
git fetch origin main
git pull origin main
# Не должно быть ошибок

# 3. Проверите virtualenv
source venv/bin/activate
pip freeze | head -5
# Должны список пакетов

# 4. Проверите Django
python manage.py check
# Должно: System check identified no issues
```

### В GitHub Actions:

1. Айте в **Actions** -> **Django CI/CD**
2. Выберите последний run
3. Проверьте **Deploy to Production** step
4. Ищите ✅ **DEPLOYMENT COMPLETED SUCCESSFULLY**

---

## 📚 СПРАВКА ПО SSH КЛЮЧАМ

### Проверить существующие ключи:

```bash
ls -la ~/.ssh/

# Должны быть:
# - id_rsa или id_ed25519 (приватный ключ)
# - id_rsa.pub или id_ed25519.pub (публичный ключ)
```

### Узнать отпечаток ключа:

```bash
ssh-keygen -l -f ~/.ssh/id_rsa
```

### Добавить ключ в ssh-agent:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa
```

---

## 🛠️ УСТРАНЕНИЕ НЕПОЛАДОК

### Если по-прежнему не работает:

```bash
# 1. Проверьте сетевую связь
ping github.com
curl -I https://github.com

# 2. Проверьте SSH соединение
ssh -T git@github.com

# 3. Проверьте права доступа
ls -la ~/.ssh/github_key
# Должно быть: -rw------- (600)

# 4. Проверьте конфиг
cat ~/.ssh/config

# 5. Включите debug режим
GIT_TRACE=1 git pull origin main

# 6. Проверьте known_hosts
cat ~/.ssh/known_hosts | grep github
```

---

## ✅ ФИНАЛЬНАЯ ПРОВЕРКА

После того как все настроено:

```bash
# 1. На GitHub push commit
git add .
git commit -m "test: verify deployment"
git push origin main

# 2. Смотрите Actions -> Deploy
# 3. Проверьте логи в "Deploy to Production" step
# 4. Ищите ✅ "DEPLOYMENT COMPLETED SUCCESSFULLY"
```

---

**Последнее обновление:** 31 декабря 2025
**Версия:** 1.0
