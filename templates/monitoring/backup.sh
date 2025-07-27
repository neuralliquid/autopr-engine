#!/bin/bash
# Backup script
set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "Creating backup at $TIMESTAMP..."

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database (if applicable)
if [ ! -z "$DATABASE_URL" ]; then
    echo "Backing up database..."
    pg_dump $DATABASE_URL > $BACKUP_DIR/db_backup_$TIMESTAMP.sql
fi

# Backup uploaded files (if applicable)
if [ -d "./uploads" ]; then
    echo "Backing up uploaded files..."
    tar -czf $BACKUP_DIR/uploads_backup_$TIMESTAMP.tar.gz ./uploads
fi

# Backup configuration
echo "Backing up configuration..."
cp .env $BACKUP_DIR/env_backup_$TIMESTAMP

echo "✅ Backup completed: $BACKUP_DIR"
