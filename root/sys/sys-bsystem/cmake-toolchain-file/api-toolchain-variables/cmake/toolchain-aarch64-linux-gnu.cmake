# toolchain-aarch64-linux-gnu.cmake
cmake_minimum_required(VERSION 3.20)

# Ідентифікація платформи
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)

# Префікс інструментів тулчейна
set(TOOLCHAIN_PREFIX "/opt/toolchains/aarch64-linux-gnu/bin/aarch64-linux-gnu-")
set(CMAKE_C_COMPILER   "${TOOLCHAIN_PREFIX}gcc")
set(CMAKE_CXX_COMPILER "${TOOLCHAIN_PREFIX}g++")
set(CMAKE_ASM_COMPILER "${TOOLCHAIN_PREFIX}gcc")

set(CMAKE_AR     "${TOOLCHAIN_PREFIX}ar"     CACHE FILEPATH "Archiver")
set(CMAKE_RANLIB "${TOOLCHAIN_PREFIX}ranlib" CACHE FILEPATH "Ranlib")
set(CMAKE_STRIP  "${TOOLCHAIN_PREFIX}strip"  CACHE FILEPATH "Strip")

# Системний корінь цільової ОС
set(CMAKE_SYSROOT "/opt/sysroots/aarch64-buildroot-linux-gnu")
set(CMAKE_FIND_ROOT_PATH "${CMAKE_SYSROOT}")

# Ізоляція пошуку
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

# Емулятор для прогону тестів CTest
set(CMAKE_CROSSCOMPILING_EMULATOR "qemu-aarch64" "-L" "${CMAKE_SYSROOT}")
