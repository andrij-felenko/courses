include(CPack)
include(CPackComponent)

# Опис компонента Runtime
cpack_add_component(Runtime
    DISPLAY_NAME "Основні програми та бібліотеки"
    DESCRIPTION "Необхідні файли для роботи сервісу."
    REQUIRED
)

# Опис компонента Development
cpack_add_component(Development
    DISPLAY_NAME "SDK для розробників"
    DESCRIPTION "Заголовочні файли та конфігурації CMake."
    DEPENDS Runtime
    GROUP SDK
)

# Опис компонента Documentation
cpack_add_component(Documentation
    DISPLAY_NAME "Документація API"
    DESCRIPTION "Повні посібники користувача та довідка з функцій."
    DISABLED
    GROUP SDK
)

# Опис групи компонентів
cpack_add_component_group(SDK
    DISPLAY_NAME "Розширення та розробка"
    DESCRIPTION "Додаткові пакети для програмістів."
    EXPANDED
)
