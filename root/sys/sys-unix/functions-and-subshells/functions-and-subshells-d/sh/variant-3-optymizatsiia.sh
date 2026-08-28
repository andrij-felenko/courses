#!/bin/bash
# Важливо: lastpipe працює лише при вимкненому Job Control (за замовчуванням у скриптах)
shopt -s lastpipe

error_count=0
cat /var/log/nginx/error.log | while read -r line; do
    case "$line" in
        *"[error]"*) error_count=$((error_count + 1)) ;;
    esac
done

echo "Total errors: $error_count" # Змінна збережена!
