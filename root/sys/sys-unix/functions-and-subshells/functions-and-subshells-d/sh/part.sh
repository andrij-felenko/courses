#!/bin/sh
error_count=0

cat /var/log/nginx/error.log | while read -r line; do
    case "$line" in
        *"[error]"*) error_count=$((error_count + 1)) ;;
    esac
done

echo "Total errors found: $error_count"
