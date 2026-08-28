# АНТИПАТЕРН: статус $? перезаписується першою ж дією
set_prompt() {
    local venv="$VIRTUAL_ENV"  # Команда local завершується з кодом 0!
    local last_exit=$?         # Тут $last_exit ЗАВЖДИ дорівнюватиме 0!
    ...
}

# ПРАВИЛЬНИЙ ШАБЛОН: миттєве збереження
set_prompt() {
    local last_exit=$?
    local pipestatus=("${PIPESTATUS[@]}")
    # Далі безпечно виконуємо будь-яку логіку
}
PROMPT_COMMAND=set_prompt
