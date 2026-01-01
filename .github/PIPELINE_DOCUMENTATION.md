# Hair Purchase Site - CI/CD Pipeline Documentation

## Overview

The new optimized CI/CD pipeline is designed for Django 5.2 LTS with:
- **Python 3.11/3.12** support
- **PostgreSQL** database testing
- **Pytest** for comprehensive testing
- **Security scanning** with Bandit & Safety
- **Code quality** checks (Black, Flake8, isort)
- **Automated deployment** to VPS

## Pipeline Stages

### 1. LINT (Code Quality)
- **Purpose**: Check code formatting and style
- **Tools**: Black, Flake8, isort
- **Status**: Non-blocking (continue on error)
- **Duration**: ~30 seconds

### 2. TEST (Functional Tests)
- **Purpose**: Run Django tests and coverage
- **Runs on**: Python 3.11 & 3.12
- **Database**: PostgreSQL 16
- **Includes**:
  - Django checks
  - Database migrations
  - Pytest with coverage
  - Static files collection
- **Duration**: ~2-3 minutes

### 3. SECURITY (Vulnerability Scan)
- **Purpose**: Detect security issues
- **Tools**: Bandit, Safety
- **Status**: Non-blocking
- **Duration**: ~1 minute

### 4. BUILD (Preparation)
- **Purpose**: Verify build can succeed
- **Checks**:
  - Dependencies can be installed
  - Static files can be collected
  - Django configuration is valid
- **Duration**: ~1 minute

### 5. DEPLOY (VPS Deployment)
- **Runs only**: On main branch, after all checks pass
- **Requirements**: SSH credentials configured
- **Steps**:
  1. Verify SSH connection
  2. Update code from Git
  3. Install dependencies
  4. Run migrations
  5. Collect static files
  6. Restart services (Gunicorn + Nginx)
  7. Health check
- **Duration**: ~3-5 minutes

## Configuration

### Required GitHub Secrets

Set these in repository Settings > Secrets and variables > Actions:

```
VPS_SSH_KEY          # Private SSH key for VPS access
VPS_HOST             # VPS IP address (e.g., 195.161.69.221)
VPS_USER             # SSH username (e.g., root)
VPS_PROJECT_PATH     # Full path to project (e.g., /home/hair_purchase)
```

### Environment Variables

**For testing (.env created automatically)**:
```
DEBUG=True
SECRET_KEY=test-secret-key
DATABASE_URL=postgresql://test_user:test_password@localhost/test_hair_db
TELEGRAM_BOT_TOKEN=test_token
TELEGRAM_ADMIN_CHAT_ID=0
```

**For VPS (.env must exist on VPS)**:
See `.env.example` - configure with real values before deployment.

## Deployment Process

### Prerequisites on VPS

1. **Repository initialized**:
   ```bash
   cd /home/hair_purchase
   git status
   ```
   If not a git repo:
   ```bash
   git init
   git remote add origin https://github.com/GiornoGiovanaJoJo/hair_purchase_site.git
   git fetch origin main
   git checkout main
   ```

2. **Virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Services configured**:
   ```bash
   sudo systemctl status gunicorn
   sudo systemctl status nginx
   ```

4. **.env configured**:
   ```bash
   cat /home/hair_purchase/.env
   # Should contain: SECRET_KEY, DATABASE_URL, TELEGRAM tokens, etc.
   ```

### Triggering Deployment

**Automatic** (on push to main):
```bash
git push origin main
# Pipeline runs automatically
```

**Manual** (re-run failed deployment):
- Go to GitHub Actions
- Select failed workflow
- Click "Re-run failed jobs"

## Monitoring

### View Pipeline Progress
- Navigate to: `github.com/GiornoGiovanaJoJo/hair_purchase_site/actions`
- Click on the workflow run
- Expand individual job to see logs

### Common Issues

#### SSH Connection Failed
```
[ERROR] ssh: connect to host 195.161.69.221 port 22: Connection refused
```
**Solutions**:
- Verify VPS_HOST is correct
- Check VPS_SSH_KEY format (should include -----BEGIN/END-----)
- Test SSH locally: `ssh -i key.pem root@VPS_IP`

#### Project Path Not Found
```
[ERROR] Project directory not found: /home/hair_purchase
```
**Solutions**:
- Verify VPS_PROJECT_PATH in secrets
- SSH into VPS and create directory: `mkdir -p /home/hair_purchase`
- Clone repo: `git clone URL /home/hair_purchase`

#### Virtual Environment Not Found
```
[ERROR] Virtual environment not found
```
**Solutions**:
```bash
cd /home/hair_purchase
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Migrations Failed
```
[ERROR] django.db.utils.OperationalError: FATAL: role "user" does not exist
```
**Solutions**:
- Check DATABASE_URL in .env on VPS
- Verify PostgreSQL is running
- Update .env with correct credentials

#### Static Files Not Serving
- Check Nginx configuration
- Verify STATIC_ROOT path is correct
- Ensure permissions are correct: `chown -R www-data:www-data /path/to/static`

## Performance Optimization

### Caching
- **Pip cache**: `cache: 'pip'` speeds up dependency installation
- **GitHub Actions**: ~1 min saved per run

### Parallel Execution
- **lint** and **test** run in parallel
- **security** runs in parallel with test
- Total time: ~5 minutes (not sequential)

## Testing Locally

### Run Tests Locally
```bash
# Install test dependencies
pip install -r requirements.txt
pip install pytest pytest-django pytest-cov

# Create .env
cp .env.example .env

# Run tests
python -m pytest --cov=. --cov-report=html -v

# Run linting
black --check .
flake8 . --max-line-length=120
isort --check-only .
```

### Test Specific Module
```bash
python -m pytest hair_app/tests/ -v
```

## Troubleshooting

### Check VPS Logs
```bash
# SSH into VPS
ssh -i key.pem root@VPS_IP

# Check Gunicorn status
sudo systemctl status gunicorn
sudo journalctl -u gunicorn -n 50

# Check Nginx status
sudo systemctl status nginx
sudo nginx -t

# Check Django logs (if configured)
tail -f /var/log/hair_purchase/django.log
```

### Verify Deployment
```bash
cd /home/hair_purchase
source venv/bin/activate
python manage.py check
python manage.py collectstatic --noinput --dry-run
```

## Future Improvements

- [ ] Add Docker image building and pushing to registry
- [ ] Implement blue-green deployment strategy
- [ ] Add automated database backups before deploy
- [ ] Add performance monitoring (APM integration)
- [ ] Add Slack/Telegram notifications for deployment status
- [ ] Implement rollback mechanism
- [ ] Add load testing before production release

## Support

For pipeline issues:
1. Check GitHub Actions logs
2. Review this documentation
3. Check VPS logs via SSH
4. Create GitHub issue with error details

---

**Last Updated**: 2026-01-01
**Pipeline Version**: 2.0 (Optimized)
