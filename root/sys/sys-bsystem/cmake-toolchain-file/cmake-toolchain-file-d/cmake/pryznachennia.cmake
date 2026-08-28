# Визначення префікса або абсолютного шляху
set(TOOLCHAIN_PREFIX "/opt/toolchains/aarch64-linux-gnu/bin/aarch64-linux-gnu-")

# Обов'язкове призначення компіляторів
set(CMAKE_C_COMPILER   "${TOOLCHAIN_PREFIX}gcc")
set(CMAKE_CXX_COMPILER "${TOOLCHAIN_PREFIX}g++")
set(CMAKE_ASM_COMPILER "${TOOLCHAIN_PREFIX}gcc")

# Допоміжні бінарні утиліти (archiver, ranlib, strip, objcopy)
set(CMAKE_AR           "${TOOLCHAIN_PREFIX}ar" CACHE FILEPATH "Archiver")
set(CMAKE_RANLIB       "${TOOLCHAIN_PREFIX}ranlib" CACHE FILEPATH "Ranlib")
set(CMAKE_STRIP        "${TOOLCHAIN_PREFIX}strip" CACHE FILEPATH "Strip")
set(CMAKE_OBJCOPY      "${TOOLCHAIN_PREFIX}objcopy" CACHE FILEPATH "Objcopy")
set(CMAKE_OBJDUMP      "${TOOLCHAIN_PREFIX}objdump" CACHE FILEPATH "Objdump")
