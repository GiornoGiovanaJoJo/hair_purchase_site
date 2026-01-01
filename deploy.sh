#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_PATH="/opt/hair_purchase_site"

echo -e "${YELLOW}🚀 Starting deployment...${NC}"

cd "$PROJECT_PATH" || exit 1

# Activate virtual environment
echo -e "${YELLOW}[0/5] Activating virtual environment...${NC}"
source venv/bin/activate || exit 1
echo -e "${GREEN}✅ Venv activated${NC}"

# 1. Git pull with GIT_TERMINAL_PROMPT=0 to prevent password prompt
echo -e "${YELLOW}[1/5] Pulling code...${NC}"
GIT_TERMINAL_PROMPT=0 git fetch origin main || exit 1
GIT_TERMINAL_PROMPT=0 git reset --hard origin/main || exit 1
echo -e "${GREEN}✅ Code pulled${NC}"

# 2. Django check
echo -e "${YELLOW}[2/5] Django check...${NC}"
python manage.py check || exit 1
echo -e "${GREEN}✅ Django OK${NC}"

# 3. Migrate
echo -e "${YELLOW}[3/5] Running migrations...${NC}"
python manage.py migrate --noinput || exit 1
echo -e "${GREEN}✅ Migrations done${NC}"

# 4. Collectstatic
echo -e "${YELLOW}[4/5] Collecting static files...${NC}"
python manage.py collectstatic --noinput --clear || exit 1
echo -e "${GREEN}✅ Static files collected${NC}"

# 5. Restart services
echo -e "${YELLOW}[5/5] Restarting services...${NC}"
sudo systemctl restart gunicorn
sudo systemctl restart nginx
echo -e "${GREEN}✅ Services restarted${NC}"

echo -e "${GREEN}🎉 Deployment completed!${NC}"
exit 0
