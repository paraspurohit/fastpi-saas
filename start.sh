#!/bin/bash

set -e  # exit on error

DOMAIN="paras.quest"
EMAIL="paraspurohit2024@gmail.com"

echo "🚀 Starting deployment for $DOMAIN"

# 1️⃣ Create required directories
echo "📁 Creating certbot directories..."
mkdir -p certbot/www
mkdir -p certbot/conf

# 2️⃣ Start FastAPI + NGINX (HTTP mode)
echo "🐳 Starting FastAPI and NGINX..."
docker compose up -d fastapi nginx

# 3️⃣ Check if certificate already exists
if [ -d "certbot/conf/live/$DOMAIN" ]; then
  echo "🔒 SSL certificate already exists. Skipping certbot."
else
  echo "🔐 Generating SSL certificate with Certbot..."
  docker compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN" -d "www.$DOMAIN"
fi

# 4️⃣ Restart NGINX to apply HTTPS config
echo "🔁 Restarting services..."
docker compose down
docker compose up -d

# 5️⃣ Final status
echo "✅ Deployment complete!"
echo "🌐 Open: https://$DOMAIN/docs"
