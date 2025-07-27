#!/bin/bash
# Health check script
set -e

echo "Checking application health..."

# Check if the application is responding
if curl -f http://localhost:3000/health > /dev/null 2>&1; then
    echo "✅ Application is healthy"
    exit 0
else
    echo "❌ Application health check failed"
    exit 1
fi
