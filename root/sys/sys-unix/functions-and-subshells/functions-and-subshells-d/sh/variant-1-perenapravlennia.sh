#!/bin/sh
error_count=0

while read -r line; do
    case "$line" in
        *"[error]"*) error_count=$((error_count + 1)) ;;
    esac
done < /var/log/nginx/error.log

echo "Total errors found: $error_count" # Працює на 100% у будь-якому sh!
