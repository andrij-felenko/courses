# Класичний синтаксис (додавання вихідних файлів)
target_sources(<ціль>
    <INTERFACE|PUBLIC|PRIVATE> [файл1...]
    [<INTERFACE|PUBLIC|PRIVATE> [файл2...] ...]
)

# Сучасний синтаксис структурованих наборів файлів (CMake 3.23+)
target_sources(<ціль>
    <INTERFACE|PUBLIC|PRIVATE>
    [FILE_SET <ім'я_набору> [TYPE <HEADERS|CXX_MODULES>]
     [BASE_DIRS <каталог_бази1...>]
     [FILES <файл1...>]]
)
