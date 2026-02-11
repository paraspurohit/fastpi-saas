#!/bin/bash
set -e

echo "Deploying latest code..."

sudo docker compose down

echo "Building containers..."
sudo docker compose build --no-cache

echo "Starting containers in detached mode..."
sudo docker compose up -d

echo "Cleaning unused images..."
sudo docker image prune -f

echo "Deployment finished successfully!"
