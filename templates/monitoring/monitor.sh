#!/bin/bash
# Monitoring script
set -e

echo "Starting application monitoring..."

# Monitor CPU and memory usage
while true; do
    echo "$(date): CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%, Memory: $(free | grep Mem | awk '{printf("%.2f%%", $3/$2 * 100.0)}')"
    sleep 30
done
