# toolchain-aarch64-linux-gnu.cmake
# Цільова операційна система та архітектура
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)

# Визначення цільового тріплета
set(TARGET_TRIPLE aarch64-linux-gnu)

# Шлях до кореневої файлової системи цільової платформи
set(TARGET_SYSROOT "/opt/sysroots/aarch64-linux-gnu")
set(CMAKE_SYSROOT "${TARGET_SYSROOT}")

# Встановлення крос-компіляторів
set(CMAKE_C_COMPILER   "${TARGET_TRIPLE}-gcc")
set(CMAKE_CXX_COMPILER "${TARGET_TRIPLE}-g++")
set(CMAKE_ASM_COMPILER "${TARGET_TRIPLE}-gcc")

# Додаткові шляхи пошуку префіксів (наприклад, сторонні залежності)
list(APPEND CMAKE_PREFIX_PATH "${TARGET_SYSROOT}/usr/local")

# Налаштування політик пошуку
set(CMAKE_FIND_ROOT_PATH "${TARGET_SYSROOT}")
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

# Додаткові прапорці лінкера для безпечного пошуку транзитивних бібліотек
set(CMAKE_EXE_LINKER_FLAGS_INIT "-Wl,-rpath-link,${TARGET_SYSROOT}/usr/lib/${TARGET_TRIPLE} -Wl,-rpath-link,${TARGET_SYSROOT}/lib/${TARGET_TRIPLE}")
set(CMAKE_SHARED_LINKER_FLAGS_INIT "-Wl,-rpath-link,${TARGET_SYSROOT}/usr/lib/${TARGET_TRIPLE} -Wl,-rpath-link,${TARGET_SYSROOT}/lib/${TARGET_TRIPLE}")
