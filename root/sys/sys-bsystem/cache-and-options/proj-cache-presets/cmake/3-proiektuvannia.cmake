cmake_minimum_required(VERSION 3.24)
project(mediasync VERSION 2.4.0 LANGUAGES C CXX)

# Встановлення обов'язкових стандартів мов програмування
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Підключення вбудованих та власних модулів розширення
include(CMakeDependentOption)
include(FeatureSummary)
include("${CMAKE_CURRENT_SOURCE_DIR}/cmake/ConfigValidation.cmake")

# ── 1. Оголошення базових прапорців конфігурації ──────────────────────────────
option(MEDIASYNC_BUILD_TOOLS "Збирати утиліти командного рядка та діагностики" ON)
option(MEDIASYNC_ENABLE_TESTS "Збирати модульні та інтеграційні тести" ON)
option(MEDIASYNC_ENABLE_LOGGING "Увімкнути детальне журналювання подій" ON)

# ── 2. Рядкові переліки з випадаючими списками (STRINGS) ───────────────────────
set(MEDIASYNC_NETWORK_BACKEND "QUIC" CACHE STRING "Мережевий протокол передачі потоків")
set_property(CACHE MEDIASYNC_NETWORK_BACKEND PROPERTY STRINGS "QUIC" "TCP" "UNIX_SOCKET")

set(MEDIASYNC_LOG_LEVEL "INFO" CACHE STRING "Мінімальний рівень деталізації журналювання")
set_property(CACHE MEDIASYNC_LOG_LEVEL PROPERTY STRINGS "DEBUG" "INFO" "WARN" "ERROR")

# ── 3. Інтроспекція системи та пошук зовнішніх залежностей ─────────────────────
find_package(Threads REQUIRED)

# Пошук бібліотеки апаратного кодування VA-API (лише для цільової платформи Linux)
if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    find_package(PkgConfig QUIET)
    if(PkgConfig_FOUND)
        pkg_check_modules(LIBVA QUIET libva)
    endif()
endif()

# Пошук фреймворку Qt6 для компіляції графічного інтерфейсу моніторингу
find_package(Qt6 QUIET COMPONENTS Core Widgets)

# ── 4. Декларація залежних опцій (CMakeDependentOption) ───────────────────────
# Апаратне прискорення через VA-API доступне лише на Linux і за наявності libva
cmake_dependent_option(
    MEDIASYNC_USE_VAAPI
    "Використовувати апаратне прискорення кодування через VA-API" ON
    "CMAKE_SYSTEM_NAME STREQUAL \"Linux\";LIBVA_FOUND" OFF
)

# Графічний монітор синхронізації активний лише якщо увімкнено утиліти і знайдено Qt6
cmake_dependent_option(
    MEDIASYNC_BUILD_GUI_MONITOR
    "Збирати графічний монітор синхронізації на базі Qt6" ON
    "MEDIASYNC_BUILD_TOOLS;Qt6_FOUND" OFF
)

# ── 5. Налаштування просунутих інженерних параметрів (ADVANCED) ───────────────
set(MEDIASYNC_RING_BUFFER_CAPACITY 65536 CACHE STRING "Розмір кільцевого буфера кадрів (у байтах)")
set(MEDIASYNC_METRICS_PORT 9090 CACHE STRING "Порт експорту телеметрії Prometheus")

mark_as_advanced(
    MEDIASYNC_RING_BUFFER_CAPACITY
    MEDIASYNC_METRICS_PORT
    LIBVA_INCLUDE_DIRS
    LIBVA_LIBRARIES
)

# ── 6. Валідація кешу перед створенням цілей збірки ────────────────────────────
mediasync_validate_cache_configuration()

# ── 7. Генерація заголовка конфігурації ────────────────────────────────────────
configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/src/config.h.in"
    "${CMAKE_CURRENT_BINARY_DIR}/include/mediasync_config.h"
    @ONLY
)

# ── 8. Створення цілей збірки та налаштування властивостей ────────────────────
add_library(mediasync_core
    src/mediasync.c
    src/mediasync.cpp
)

target_include_directories(mediasync_core
    PUBLIC
        "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
        "$<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}/include>"
        "$<INSTALL_INTERFACE:include>"
)

target_link_libraries(mediasync_core
    PUBLIC
        Threads::Threads
)

if(MEDIASYNC_USE_VAAPI)
    target_include_directories(mediasync_core PRIVATE ${LIBVA_INCLUDE_DIRS})
    target_link_libraries(mediasync_core PRIVATE ${LIBVA_LIBRARIES})
endif()

# Генерація підсумкового звіту про стан усіх модулів
feature_summary(
    WHAT ALL 
    INCLUDE_QUIET_PACKAGES 
    DESCRIPTION "=== Підсумковий звіт конфігурації mediasync ==="
)
