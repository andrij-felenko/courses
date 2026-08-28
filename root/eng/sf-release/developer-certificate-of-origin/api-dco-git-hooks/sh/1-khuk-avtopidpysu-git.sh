#!/bin/sh
# .git/hooks/prepare-commit-msg
# Автоматичне додавання Signed-off-by трейлера, якщо його ще немає

COMMIT_MSG_FILE="$1"
COMMIT_SOURCE="$2"

# Не модифікуємо автоматичні повідомлення злиттів (merge) або squash-комітів
if [ "$COMMIT_SOURCE" = "merge" ] || [ "$COMMIT_SOURCE" = "squash" ]; then
    exit 0
fi

NAME=$(git config user.name)
EMAIL=$(git config user.email)

if [ -z "$NAME" ] || [ -z "$EMAIL" ]; then
    echo "ПОМИЛКА: git config user.name або user.email не налаштовано!" >&2
    exit 1
fi

SOB_LINE="Signed-off-by: $NAME <$EMAIL>"

# Перевіряємо, чи підпис уже присутній у файлі
if ! grep -qs "^$SOB_LINE" "$COMMIT_MSG_FILE"; then
    # Додаємо порожній рядок і трейлер у кінець повідомлення
    printf "\n%s\n" "$SOB_LINE" >> "$COMMIT_MSG_FILE"
fi
