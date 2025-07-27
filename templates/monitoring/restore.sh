#!/bin/bash
# Restore script
set -e

BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

echo "Restoring from backup: $BACKUP_FILE"

# Restore database
if [[ $BACKUP_FILE == *.sql ]]; then
    echo "Restoring database..."
    psql $DATABASE_URL < $BACKUP_FILE
fi

# Restore files
if [[ $BACKUP_FILE == *.tar.gz ]]; then
    echo "Restoring files..."
    tar -xzf $BACKUP_FILE
fi

echo "✅ Restore completed"
