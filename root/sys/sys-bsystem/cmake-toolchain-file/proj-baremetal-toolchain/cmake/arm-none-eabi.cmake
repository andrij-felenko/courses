# cmake/arm-none-eabi.cmake
cmake_minimum_required(VERSION 3.20)

# 1. Декларація цільової платформи без операційної системи
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR arm)

# 2. Обхід помилки лінкування під час перевірки компілятора в project()
# Замість створення повноцінного ELF CMake перевірятиме компілятор через архіватор .a
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

# 3. Виявлення префікса цільового тулчейна
set(TOOLCHAIN_TRIPLE "arm-none-eabi")

# Підтримка пошуку в системному PATH або за фіксованим префіксом змінної середовища
if(DEFINED ENV{ARM_TOOLCHAIN_PATH})
    set(TOOLCHAIN_BIN_DIR "$ENV{ARM_TOOLCHAIN_PATH}/bin/")
else()
    set(TOOLCHAIN_BIN_DIR "")
endif()

# 4. Призначення компіляторів та бінарних утиліт
set(CMAKE_C_COMPILER   "${TOOLCHAIN_BIN_DIR}${TOOLCHAIN_TRIPLE}-gcc")
set(CMAKE_CXX_COMPILER "${TOOLCHAIN_BIN_DIR}${TOOLCHAIN_TRIPLE}-g++")
set(CMAKE_ASM_COMPILER "${TOOLCHAIN_BIN_DIR}${TOOLCHAIN_TRIPLE}-gcc")

set(CMAKE_AR       "${TOOLCHAIN_BIN_DIR}${TOOLCHAIN_TRIPLE}-ar"      CACHE FILEPATH "Archiver")
set(CMAKE_RANLIB   "${TOOLCHAIN_BIN_DIR}${TOOLCHAIN_TRIPLE}-ranlib"  CACHE FILEPATH "Ranlib")
set(CMAKE_OBJCOPY  "${TOOLCHAIN_BIN_DIR}${TOOLCHAIN_TRIPLE}-objcopy" CACHE FILEPATH "Objcopy")
set(CMAKE_OBJDUMP  "${TOOLCHAIN_BIN_DIR}${TOOLCHAIN_TRIPLE}-objdump" CACHE FILEPATH "Objdump")
set(CMAKE_SIZE     "${TOOLCHAIN_BIN_DIR}${TOOLCHAIN_TRIPLE}-size"    CACHE FILEPATH "Size utility")

# 5. Ізоляція пошукових шляхів: інструменти шукаємо на хості, бібліотеки хоста блокуємо
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
