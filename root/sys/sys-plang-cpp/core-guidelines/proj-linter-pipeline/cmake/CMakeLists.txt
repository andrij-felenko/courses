cmake_minimum_required(VERSION 3.22)
project(CoreGuidelinesProject CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Експорт бази компіляції (compile_commands.json) для лінтерів
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_program(CLANG_TIDY_EXE NAMES clang-tidy)

if(CLANG_TIDY_EXE)
    message(STATUS "Clang-Tidy активовано: ${CLANG_TIDY_EXE}")
    set(CMAKE_CXX_CLANG_TIDY 
        "${CLANG_TIDY_EXE};--config-file=${CMAKE_CURRENT_SOURCE_DIR}/.clang-tidy;--warnings-as-errors=*")
else()
    message(WARNING "Clang-Tidy не знайдено на машині розробника!")
endif()

add_library(telemetry_lib src/telemetry_filter.cpp)
add_executable(telemetry_app src/main.cpp)
target_link_libraries(telemetry_app PRIVATE telemetry_lib)
