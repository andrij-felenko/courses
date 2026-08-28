# arm-none-eabi.cmake — націлює CMake на bare-metal Cortex-M0.
set(CMAKE_SYSTEM_NAME Generic)          # «Generic» = немає ОС на цільовій системі
set(CMAKE_SYSTEM_PROCESSOR arm)

set(TOOLCHAIN arm-none-eabi)
set(CMAKE_C_COMPILER   ${TOOLCHAIN}-gcc)
set(CMAKE_ASM_COMPILER ${TOOLCHAIN}-gcc)
set(CMAKE_CXX_COMPILER ${TOOLCHAIN}-g++)
set(CMAKE_OBJCOPY      ${TOOLCHAIN}-objcopy CACHE INTERNAL "")
set(CMAKE_SIZE         ${TOOLCHAIN}-size    CACHE INTERNAL "")

# КЛЮЧОВЕ: прапорці ядра. Cortex-M0 = архітектура ARMv6-M, набір інструкцій Thumb.
set(CPU_FLAGS "-mcpu=cortex-m0 -mthumb")

# Не намагайся лінкувати тестову програмку при перевірці компілятора:
# на bare-metal їй нема куди «запуститися», тож CMake інакше вирішить, що компілятор зламаний.
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)
