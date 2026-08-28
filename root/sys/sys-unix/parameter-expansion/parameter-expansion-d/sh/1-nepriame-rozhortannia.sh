ENV="PRODUCTION"
DB_HOST_DEVELOPMENT="127.0.0.1"
DB_HOST_PRODUCTION="10.0.100.5"

# Формуємо динамічне ім'я цільової змінної:
TARGET_VAR="DB_HOST_${ENV}"

# Отримуємо значення через непряме розгортання:
echo "${!TARGET_VAR}"
# Вивід: "10.0.100.5"
