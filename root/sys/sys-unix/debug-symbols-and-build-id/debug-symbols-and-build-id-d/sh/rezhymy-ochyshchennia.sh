# 1. Повне очищення (за замовчуванням): видаляє .symtab, .strtab та всі .debug_*
strip /usr/bin/app

# 2. Видалення виключно секцій DWARF зі збереженням локальних символів .symtab
strip --strip-debug /usr/bin/app

# 3. Видалення символів, не потрібних для обробки релокацій (стандарт збірки дистрибутивів)
strip --strip-unneeded /usr/lib/libcustom.so

# 4. Видалення специфічних секцій метаданих
strip -R .comment -R .note.ABI-tag /usr/bin/app
