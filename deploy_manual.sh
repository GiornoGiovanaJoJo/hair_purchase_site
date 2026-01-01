#!/bin/bash

echo "🚀 Starting manual deployment..."

# Navigate to project directory
cd /opt/hair_purchase_site || exit 1

# Check Python version
echo "Checking Python..."
python3 --version

# Create virtual environment if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Remove cached files
echo "Removing cached files..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
rm -rf staticfiles/ 2>/dev/null || true

# Run migrations
echo "Running migrations..."
python3 manage.py migrate

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput

# Kill any existing gunicorn processes
echo "Killing existing processes..."
pkill -f gunicorn || true
sleep 2

# Start gunicorn
echo "Starting Gunicorn..."
gunicorn --workers 3 --bind 0.0.0.0:8000 --timeout 120 config.wsgi:application &
sleep 3

# Restart nginx
echo "Restarting Nginx..."
sudo systemctl restart nginx || sudo service nginx restart

echo "✅ Deployment complete!"
echo "Application should be running at: http://195.161.69.221"
echo "Check with: curl http://localhost:8000"
