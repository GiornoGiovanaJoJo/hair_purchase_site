#!/bin/bash

echo "🔍 DEBUGGING SERVER..."
echo ""

echo "1️⃣ Check if gunicorn is running:"
ps aux | grep gunicorn | grep -v grep
echo ""

echo "2️⃣ Check nginx status:"
sudo systemctl status nginx --no-pager | head -20
echo ""

echo "3️⃣ Check port 8000:"
netstat -tulpn | grep 8000 || echo "Port 8000 not listening"
echo ""

echo "4️⃣ Test localhost:8000:"
curl -s http://localhost:8000 | head -20
echo ""

echo "5️⃣ Test API endpoint:"
curl -s -X POST http://localhost:8000/api/calculate-price/ \
  -H "Content-Type: application/json" \
  -d '{"hair_color":"blonde","hair_length":60,"hair_structure":"slavyanka","hair_age":0,"hair_condition":"excellent"}' | head -50
echo ""

echo "6️⃣ Django logs (last 50 lines):"
tail -50 /var/log/gunicorn.log 2>/dev/null || echo "No gunicorn log"
echo ""

echo "7️⃣ Nginx error log (last 20 lines):"
sudo tail -20 /var/log/nginx/error.log 2>/dev/null || echo "No nginx error log"
