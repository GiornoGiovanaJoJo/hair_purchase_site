#!/bin/bash

# Скрипт для автоматического деплоя на продакшн

set -e

echo "🚀 Starting deployment..."

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo "Please create .env file with required variables"
    exit 1
fi

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Error: Docker is not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Error: Docker Compose is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Environment checks passed${NC}"

# Остановка старых контейнеров
echo -e "${YELLOW}🛑 Stopping old containers...${NC}"
docker-compose down

# Получение последних изменений
echo -e "${YELLOW}🔄 Pulling latest changes from Git...${NC}"
git pull origin main

# Сборка Docker образов
echo -e "${YELLOW}📦 Building Docker images...${NC}"
docker-compose build --no-cache

# Запуск контейнеров
echo -e "${YELLOW}🚀 Starting containers...${NC}"
docker-compose up -d

# Ожидание запуска базы данных
echo -e "${YELLOW}⏳ Waiting for database...${NC}"
sleep 5

# Применение миграций
echo -e "${YELLOW}💾 Running migrations...${NC}"
docker-compose exec -T web python manage.py migrate --noinput

# Сбор статики
echo -e "${YELLOW}📁 Collecting static files...${NC}"
docker-compose exec -T web python manage.py collectstatic --noinput

# Проверка статуса контейнеров
echo -e "${YELLOW}🔍 Checking container status...${NC}"
docker-compose ps

# Проверка здоровья приложения
echo -e "${YELLOW}🏥 Checking application health...${NC}"
sleep 3

if curl -f http://localhost:8000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo -e "${GREEN}🎉 Application is running at http://localhost:8000${NC}"
else
    echo -e "${RED}❌ Warning: Application may not be responding${NC}"
    echo "Check logs with: docker-compose logs web"
fi

# Показать логи (последние 20 строк)
echo -e "${YELLOW}📜 Recent logs:${NC}"
docker-compose logs --tail=20

echo -e "${GREEN}✅ Deployment completed!${NC}"
echo -e "${YELLOW}Useful commands:${NC}"
echo "  docker-compose logs -f web      # View web logs"
echo "  docker-compose logs -f bot      # View bot logs"
echo "  docker-compose ps               # Check container status"
echo "  docker-compose restart web      # Restart web container"
