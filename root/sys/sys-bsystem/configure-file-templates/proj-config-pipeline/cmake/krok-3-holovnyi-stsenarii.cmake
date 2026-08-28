cmake_minimum_required(VERSION 3.20)
project(DiagnosticsTool VERSION 2.4.1 LANGUAGES C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Оголошення опцій користувача, які потрапляють у кеш збірки
option(DIAG_ENABLE_ZSTD "Увімкнути підтримку стиснення Zstandard" ON)
option(DIAG_ENABLE_TRACING "Увімкнути детальне діагностичне трасування" OFF)
option(DIAG_ENABLE_AVX512 "Активація апаратних інструкцій AVX-512" OFF)

set(DIAG_BUFFER_SIZE 8192 CACHE STRING "Розмір внутрішнього буфера журналів")

# Підключення модуля вилучення даних Git
include(cmake/GetGitRevision.cmake)

# Визначення шляху до ізольованого каталогу згенерованих заголовків
set(GENERATED_INCLUDE_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated/include")

# Генерація файлу препроцесорних директив (config.h)
configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/include/diag/config.h.in"
    "${GENERATED_INCLUDE_DIR}/diag/config.h"
    @ONLY
)

# Генерація файлу типізованих констант C++ (version.hpp)
configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/include/diag/version.hpp.in"
    "${GENERATED_INCLUDE_DIR}/diag/version.hpp"
    @ONLY
)

# Створення бібліотеки ядра
add_library(diag_core STATIC)

# Експорт шляхів до заголовків через генераторні вирази вимог вжитку
target_include_directories(diag_core PUBLIC
    $<BUILD_INTERFACE:${GENERATED_INCLUDE_DIR}>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# Створення демонстраційних утиліт на C та C++
add_executable(diag_cli_c src/main.c)
target_link_libraries(diag_cli_c PRIVATE diag_core)

add_executable(diag_cli_cpp src/main.cpp)
target_link_libraries(diag_cli_cpp PRIVATE diag_core)
