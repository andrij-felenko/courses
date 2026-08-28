# Формування аргументів компілятора або утиліти:
VERBOSE="1"
DEBUG_FLAG="${VERBOSE:+--verbose}"
# Результат: DEBUG_FLAG набуває значення "--verbose"

unset VERBOSE
DEBUG_FLAG="${VERBOSE:+--verbose}"
# Результат: DEBUG_FLAG набуває значення ""

# Використання у виклику програми без утворення порожніх аргументів:
curl ${AUTH_TOKEN:+-H "Authorization: Bearer $AUTH_TOKEN"} "https://api.internal/data"
