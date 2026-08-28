# Ідіома 1: Явне збереження коду повернення через логічне "АБО"
status=0
grep -q "admin_user" /etc/passwd || status=$?

if [[ ${status} -eq 0 ]]; then
    echo "Користувача знайдено."
elif [[ ${status} -eq 1 ]]; then
    echo "Користувача не знайдено (штатна ситуація)."
else
    echo "Критичний збій доступу до файлу: ${status}" >&2
    exit "${status}"
fi

# Ідіома 2: Використання всередині блоку if (errexit автоматично придушується)
if grep -q "admin_user" /etc/passwd; then
    echo "Знайдено."
fi
