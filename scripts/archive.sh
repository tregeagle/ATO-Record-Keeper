#!/usr/bin/env bash
set -euo pipefail

ARCHIVE_DIR=".archive"
MAX_BACKUPS=3
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_NAME="backup-${TIMESTAMP}.tar.gz"

mkdir -p "$ARCHIVE_DIR"

echo "Archiving input/ and imports/ to ${ARCHIVE_DIR}/${BACKUP_NAME}..."
tar -czf "${ARCHIVE_DIR}/${BACKUP_NAME}" input/ imports/ 2>/dev/null || {
    echo "Error: failed to create archive" >&2
    exit 1
}

echo "Created ${ARCHIVE_DIR}/${BACKUP_NAME}"

# Remove old backups, keeping only the last $MAX_BACKUPS
NUM_BACKUPS=$(ls -1t "${ARCHIVE_DIR}"/backup-*.tar.gz 2>/dev/null | wc -l)
if [ "$NUM_BACKUPS" -gt "$MAX_BACKUPS" ]; then
    ls -1t "${ARCHIVE_DIR}"/backup-*.tar.gz | tail -n +"$((MAX_BACKUPS + 1))" | xargs rm -f
    REMOVED=$((NUM_BACKUPS - MAX_BACKUPS))
    echo "Removed ${REMOVED} old backup(s), keeping last ${MAX_BACKUPS}"
fi

echo "Done. Current backups:"
ls -lh "${ARCHIVE_DIR}"/backup-*.tar.gz
