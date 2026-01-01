# CI/CD Pipeline - Quick Start Guide

## 30 Seconds Setup

### 1. Add GitHub Secrets

Go to: **Settings > Secrets and variables > Actions > New repository secret**

Add these 4 secrets:

| Secret Name | Value | Example |
|------------|-------|----------|
| `VPS_SSH_KEY` | Your private SSH key | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `VPS_HOST` | VPS IP address | `195.161.69.221` |
| `VPS_USER` | SSH username | `root` |
| `VPS_PROJECT_PATH` | Project path on VPS | `/home/hair_purchase` |

**How to get SSH key**:
```bash
# On your local machine
cat ~/.ssh/id_rsa
# Copy entire content starting from "-----BEGIN" to "-----END"
```

### 2. Verify VPS Setup

SSH into your VPS and run:

```bash
ssh root@195.161.69.221

# Check if project exists
ls -la /home/hair_purchase/

# Check if it's a git repo
cd /home/hair_purchase
git status

# Check venv
ls -la venv/

# Check services
sudo systemctl status gunicorn
sudo systemctl status nginx
```

**If any of these fail, run the full setup below.**

### 3. Push Code

```bash
git push origin main
```

Pipeline will automatically run!

---

## Full VPS Setup (If Needed)

### For Fresh VPS Installation

```bash
# 1. SSH into VPS
ssh root@195.161.69.221

# 2. Create project directory
mkdir -p /home/hair_purchase
cd /home/hair_purchase

# 3. Clone repository
git clone https://github.com/GiornoGiovanaJoJo/hair_purchase_site.git .

# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 6. Create .env file
cat > .env << 'EOF'
DEBUG=False
SECRET_KEY=your-django-secret-key-here
ALLOWED_HOSTS=4895c9d9450e.vps.myjino.ru,localhost,127.0.0.1
DATABASE_URL=
TELEGRAM_BOT_TOKEN=your-token
TELEGRAM_ADMIN_CHAT_ID=your-id
CORS_ALLOW_ALL=False
EOF

# 7. Run migrations
python manage.py migrate

# 8. Collect static files
python manage.py collectstatic --noinput

# 9. Create systemd service for Gunicorn
sudo tee /etc/systemd/system/gunicorn.service > /dev/null << 'EOF'
[Unit]
Description=Gunicorn service
After=network.target

[Service]
Type=notify
User=root
WorkingDirectory=/home/hair_purchase
Environment="PATH=/home/hair_purchase/venv/bin"
ExecStart=/home/hair_purchase/venv/bin/gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 60
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
KillSignal=SIGTERM
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# 10. Enable and start Gunicorn
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn

# 11. Test site
curl http://localhost:8000
```

---

## Monitoring Pipeline

### 1. View Live Progress
- Go to: `https://github.com/GiornoGiovanaJoJo/hair_purchase_site/actions`
- Click on the latest workflow run
- Watch jobs execute in real-time

### 2. Understand Job Status

```
LINT          [✓ Passed]  - Code style is OK
TEST          [✓ Passed]  - All tests pass
SECURITY      [✓ Passed]  - No vulnerabilities
BUILD         [✓ Passed]  - Can build successfully
DEPLOY        [✓ Passed]  - Deployed to VPS!
```

### 3. If Deployment Fails

**Check VPS manually**:
```bash
ssh root@195.161.69.221
cd /home/hair_purchase
sudo systemctl status gunicorn
sudo journalctl -u gunicorn -n 50
```

**Check GitHub Actions logs**:
1. Go to failed workflow
2. Click "Deploy to VPS" job
3. Expand logs to see error message

---

## Common Commands

### SSH into VPS
```bash
ssh root@195.161.69.221
```

### Check Deployment Status
```bash
cd /home/hair_purchase
source venv/bin/activate
python manage.py check
```

### View Service Logs
```bash
# Gunicorn
sudo journalctl -u gunicorn -f

# Nginx
sudo tail -f /var/log/nginx/error.log
```

### Restart Services
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### Verify Site is Working
```bash
curl https://4895c9d9450e.vps.myjino.ru
```

---

## Troubleshooting Quick Links

- **SSH Connection Failed** → Check `VPS_SSH_KEY` secret format
- **Project Not Found** → Verify `VPS_PROJECT_PATH` secret
- **Migrations Failed** → Check `DATABASE_URL` in .env on VPS
- **Static Files Not Loading** → Check Nginx configuration
- **Site 502 Error** → Check Gunicorn logs: `sudo systemctl status gunicorn`

**Full documentation**: See `PIPELINE_DOCUMENTATION.md`

---

## What Happens on Push

```mermaid
git push origin main
      |
      v
[LINT] Code quality checks
      |                    
      +----[TEST] Django tests (Python 3.11 & 3.12)
      |                    
      +----[SECURITY] Vulnerability scan
      |
      v
   [BUILD] Verify build
      |
      v
  [DEPLOY] SSH to VPS -> Git pull -> Migrations -> Restart services
      |
      v
[HEALTH CHECK] Verify site is up
```

---

## Questions?

1. Read full docs: `.github/PIPELINE_DOCUMENTATION.md`
2. Check GitHub Actions: `Actions` tab in repository
3. SSH into VPS and check logs
4. Create GitHub issue with error details

**Happy deploying!** 🚀
