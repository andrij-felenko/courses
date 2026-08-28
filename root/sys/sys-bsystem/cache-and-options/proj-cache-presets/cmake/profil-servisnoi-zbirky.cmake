# Фіксація компіляторів для відтворюваності оточення
set(CMAKE_C_COMPILER "clang" CACHE FILEPATH "Компілятор C для серверів CI" FORCE)
set(CMAKE_CXX_COMPILER "clang++" CACHE FILEPATH "Компілятор C++ для серверів CI" FORCE)

# Фіксація типу збірки та оптимізацій
set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Оптимізована продуктивна збірка" FORCE)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON CACHE BOOL "Експорт компіляційної бази" FORCE)

# Конфігурація модулів проєкту
set(MEDIASYNC_BUILD_TOOLS ON CACHE BOOL "Збирати утиліти" FORCE)
set(MEDIASYNC_ENABLE_TESTS ON CACHE BOOL "Збирати модульні тести" FORCE)
set(MEDIASYNC_ENABLE_LOGGING ON CACHE BOOL "Журналювання увімкнено" FORCE)
set(MEDIASYNC_LOG_LEVEL "INFO" CACHE STRING "Рівень журналювання" FORCE)
set(MEDIASYNC_NETWORK_BACKEND "QUIC" CACHE STRING "Протокол за замовчуванням" FORCE)
set(MEDIASYNC_RING_BUFFER_CAPACITY 262144 CACHE STRING "Буфер 256 КБ для високошвидкісних каналів" FORCE)
