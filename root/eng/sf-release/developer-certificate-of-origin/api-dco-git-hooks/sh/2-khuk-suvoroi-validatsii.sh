#!/bin/sh
# .git/hooks/commit-msg
# Сувора валідація наявності DCO підпису перед створенням об'єкта коміту

MSG_FILE="$1"
AUTHOR_EMAIL=$(git config user.email)

# Шукаємо валідний рядок Signed-off-by за стандартом RFC 5322
SOB_REGEX="^Signed-off-by: .+ <[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}>$"

if ! grep -Eqs "$SOB_REGEX" "$MSG_FILE"; then
    echo "================================================================" >&2
    echo "ПОМИЛКА КОМПЛАЄНСУ DCO: Повідомлення коміту не містить підпису!" >&2
    echo "Будь ласка, використовуйте прапорець: git commit -s" >&2
    echo "Очікуваний формат: Signed-off-by: Ім'я Прізвище <email@domain>" >&2
    echo "================================================================" >&2
    exit 1
fi

# Перевіряємо збіг пошти автора з поштою у знайденому підписі
if ! grep -qs "<$AUTHOR_EMAIL>" "$MSG_FILE"; then
    echo "ПОМИЛКА: Email у Signed-off-by не збігається з git config user.email ($AUTHOR_EMAIL)!" >&2
    exit 1
fi

exit 0
