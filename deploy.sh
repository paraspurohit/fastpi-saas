#!/bin/bash
set -e

echo "🚀 Deploying latest code..."


sudo docker compose up -d fastapi nginx

echo "✅ Deployment finished"
