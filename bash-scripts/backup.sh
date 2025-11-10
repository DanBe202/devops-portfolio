#!/bin/bash

SOURCE_DIR=$1
BACKUP_DIR=$2
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_NAME="backup_$TIMESTAMP.tar.gz"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"
LOG_FILE="$BACKUP_DIR/backup.log"
MAX_BACKUPS=5

if [ -z "$SOURCE_DIR" ] || [ -z "$BACKUP_DIR" ]; then
    echo "Usage: $0 <source_directory> <backup_directory>"
    exit 1
fi

mkdir -p "$BACKUP_DIR"

echo "Starting backup of $SOURCE_DIR to $BACKUP_PATH at $(date)" >> "$LOG_FILE"

tar -czf "$BACKUP_PATH" "$SOURCE_DIR"

if [ $? -eq 0 ]; then
    echo "Backup successful: $BACKUP_NAME" >> "$LOG_FILE"
else
    echo "Backup failed" >> "$LOG_FILE"
    exit 1
fi

BACKUP_COUNT=$(ls -1 "$BACKUP_DIR" | grep -E "^backup_.*\.tar\.gz$" | wc -l)

if [ "$BACKUP_COUNT" -gt "$MAX_BACKUPS" ]; then
    NUM_TO_DELETE=$((BACKUP_COUNT - MAX_BACKUPS))
    echo "Cleaning up old backups..." >> "$LOG_FILE"
    
    ls -1t "$BACKUP_DIR" | grep -E "^backup_.*\.tar\.gz$" | tail -n "$NUM_TO_DELETE" | while read -r OLD_BACKUP; do
        echo "Deleting $OLD_BACKUP" >> "$LOG_FILE"
        rm -f "$BACKUP_DIR/$OLD_BACKUP"
    done
fi

echo "Backup process finished at $(date)" >> "$LOG_FILE"
echo "--------------------------------" >> "$LOG_FILE"