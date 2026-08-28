# Збереження поточної активної пастки для сигналу SIGINT
OLD_INT_TRAP=$(trap -p INT)

# Встановлення тимчасового локального обробника
trap 'echo "Операцію перервано користувачем"; return 1' INT

# Виконання критичної операції
perform_sensitive_io_operation

# Відновлення початкової пастки (або скидання, якщо пастки не було)
if [[ -n "${OLD_INT_TRAP}" ]]; then
    eval "${OLD_INT_TRAP}"
else
    trap - INT
fi
