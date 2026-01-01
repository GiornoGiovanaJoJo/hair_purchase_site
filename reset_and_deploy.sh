#!/bin/bash

# Stop the current Django application
echo "Stopping Django application..."
sudo systemctl stop hair-purchase || true

# Navigate to project directory
cd /opt/hair_purchase_site || exit 1

# Remove old static files
echo "Removing cached static files..."
sudo rm -rf staticfiles/ || true
sudo rm -rf /var/www/hair_purchase/static/* || true

# Remove Python cache
echo "Removing Python cache..."
find . -type d -name __pycache__ -exec rm -rf {} + || true
find . -type f -name "*.pyc" -delete || true

# Clear Django cache
echo "Clearing Django cache..."
python manage.py shell << EOF
from django.core.cache import cache
cache.clear()
print("Django cache cleared")
EOF

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Restart the application
echo "Restarting Django application..."
sudo systemctl start hair-purchase
sudo systemctl restart nginx

echo "✅ Deployment complete!"
sudo systemctl status hair-purchase
