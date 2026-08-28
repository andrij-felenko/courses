# Підхід 1: Тимчасове вимкнення pipefail для конкретного конвеєра
set +o pipefail
data_stream | head -n 10
set -o pipefail

# Підхід 2: Явна обробка масиву PIPESTATUS у Bash
data_stream | head -n 10 || true
status=("${PIPESTATUS[@]}")
# status[0] містить 141 (SIGPIPE), status[1] містить 0 (head успішний)
if [[ "${status[1]}" -eq 0 ]]; then
    echo "Перші 10 рядків успішно отримано"
fi
