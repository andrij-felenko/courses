# Перевірка наявності та типу Build ID
readelf -n /usr/bin/app | grep "Build ID"

# Перегляд усіх секцій бінарника (пошук .symtab та .debug_*)
readelf -S /usr/bin/app

# Перевірка статусу бінарника (stripped / not stripped)
file /usr/bin/app

# Ручне завантаження DWARF-файлу за відомим Build ID через debuginfod
debuginfod-find debuginfo 7a9f1b2c4d8e3f015a6b7c8d9e0f1a2b3c4d5e6f

# Перевірка зв'язку між очищеним бінарником і його символами
eu-unstrip -n -e /usr/bin/app
