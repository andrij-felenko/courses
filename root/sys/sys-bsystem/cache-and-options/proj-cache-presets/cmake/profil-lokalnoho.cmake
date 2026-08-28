# Базовий налагоджувальний режим
set(CMAKE_BUILD_TYPE "Debug" CACHE STRING "Налагоджувальна збірка" FORCE)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON CACHE BOOL "Експорт бази компіляції для інтеграції з clangd" FORCE)

# Ін'єкція прапорців динамічних санітайзерів пам'яті
set(CMAKE_C_FLAGS_DEBUG "-g -O1 -fsanitize=address,undefined -fno-omit-frame-pointer" CACHE STRING "Прапорці C для ASan" FORCE)
set(CMAKE_CXX_FLAGS_DEBUG "-g -O1 -fsanitize=address,undefined -fno-omit-frame-pointer" CACHE STRING "Прапорці C++ для ASan" FORCE)

# Налаштування модулів для локальної розробки
set(MEDIASYNC_BUILD_TOOLS ON CACHE BOOL "Збирати утиліти тестування" FORCE)
set(MEDIASYNC_ENABLE_TESTS ON CACHE BOOL "Збирати тестовий набір" FORCE)
set(MEDIASYNC_ENABLE_LOGGING ON CACHE BOOL "Детальне журналювання" FORCE)
set(MEDIASYNC_LOG_LEVEL "DEBUG" CACHE STRING "Максимальна деталізація подій" FORCE)
set(MEDIASYNC_NETWORK_BACKEND "UNIX_SOCKET" CACHE STRING "Локальний транспорт сокетів" FORCE)
set(MEDIASYNC_RING_BUFFER_CAPACITY 4096 CACHE STRING "Мінімальний буфер для провокування швидкого переповнення в тестах" FORCE)
