(
    # Очищаємо успадкований стек батька та ініціалізуємо власний обробник
    __DEFER_STACK=()
    __DEFER_RUNNING=0
    defer_init

    defer_mktemp_dir SUBSHELL_TMP "subjob"
    echo "Локальна робота в ${SUBSHELL_TMP}..."
    # При виході з дужок ( ... ) відпрацює локальний defer, видаливши SUBSHELL_TMP
)
