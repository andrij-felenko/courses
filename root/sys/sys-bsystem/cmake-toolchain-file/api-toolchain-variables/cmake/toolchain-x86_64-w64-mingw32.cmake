# toolchain-x86_64-w64-mingw32.cmake
cmake_minimum_required(VERSION 3.20)

# Ідентифікація платформи Windows
set(CMAKE_SYSTEM_NAME Windows)
set(CMAKE_SYSTEM_PROCESSOR x86_64)

# Префікс інструментів MinGW
set(TOOLCHAIN_PREFIX "x86_64-w64-mingw32-")
set(CMAKE_C_COMPILER   "${TOOLCHAIN_PREFIX}gcc")
set(CMAKE_CXX_COMPILER "${TOOLCHAIN_PREFIX}g++")
set(CMAKE_RC_COMPILER  "${TOOLCHAIN_PREFIX}windres")

# Каталог розташування заголовків та бібліотек MinGW
set(CMAKE_FIND_ROOT_PATH "/usr/x86_64-w64-mingw32")

# Маршрутизація пошуку
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

# Емулятор для виконання Windows-тестів на Linux
set(CMAKE_CROSSCOMPILING_EMULATOR "wine64")
