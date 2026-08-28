# Фільтрація по списку слів за префіксом "st"
compgen -W "start status stop restart reload" -- "st"
# Вивід:
# start
# status
# stop

# Пошук активних користувачів на літеру "r"
compgen -u -- "r"
# Вивід:
# root
# rpc

# Пошук змінних оточення, що починаються з "LC_"
compgen -v -- "LC_"
# Вивід:
# LC_ALL
# LC_CTYPE
# LC_MESSAGES

# Доповнення файлів з фільтрацією виключень: залишаємо лише файли C/C++
compgen -f -X '!*.@(c|cpp|cc|h|hpp)' -- "src/m"
