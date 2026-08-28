cmake_minimum_required(VERSION 3.24)
project(telemetry_service LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Глобальне вимкнення оновлень для швидкості повторних конфігурацій
set(FETCHCONTENT_UPDATES_DISCONNECTED ON CACHE BOOL "" FORCE)

include(FetchContent)

# 1. Ізоляція опцій підпроєктів: вимикаємо зайві компоненти до завантаження
set(FMT_TEST OFF CACHE BOOL "Disable fmt tests" FORCE)
set(FMT_DOC OFF CACHE BOOL "Disable fmt docs" FORCE)
set(FMT_INSTALL OFF CACHE BOOL "Disable fmt install targets" FORCE)

set(JSON_BuildTests OFF CACHE BOOL "Disable nlohmann_json tests" FORCE)
set(JSON_Install OFF CACHE BOOL "Disable nlohmann_json install" FORCE)

# 2. Декларація залежностей із фіксацією хешів SHA-256 та перенаправленням на find_package
FetchContent_Declare(
    fmt
    URL                https://github.com/fmtlib/fmt/archive/refs/tags/10.2.1.tar.gz
    URL_HASH           SHA256=312e4997a80e220502f2558fb3b3797b9aeded05dce4018204b3b47172327145
    FIND_PACKAGE_ARGS  10.2 CONFIG
)

FetchContent_Declare(
    nlohmann_json
    URL                https://github.com/nlohmann/json/archive/refs/tags/v3.11.3.tar.gz
    URL_HASH           SHA256=0d8eed583a45371694f4c9a4891158229c1598f804fc921e51381283c7ce353c
    FIND_PACKAGE_ARGS  3.11 CONFIG
)

# 3. Активація підпроєктів (автоматично викликає add_subdirectory з EXCLUDE_FROM_ALL)
FetchContent_MakeAvailable(fmt nlohmann_json)

# 4. Оголошення головного виконуваного файлу
add_executable(telemetry_service
    src/main.cpp
    src/collector.cpp
)

# 5. Налаштування найсуворіших попереджень для власного коду
if(MSVC)
    target_compile_options(telemetry_service PRIVATE /W4 /WX /permissive-)
else()
    target_compile_options(telemetry_service PRIVATE -Wall -Wextra -Wpedantic -Werror)
endif()

# 6. Лінкування з цілями підпроєктів: заголовки імпортуються як системні
target_link_libraries(telemetry_service PRIVATE
    fmt::fmt
    nlohmann_json::nlohmann_json
)
