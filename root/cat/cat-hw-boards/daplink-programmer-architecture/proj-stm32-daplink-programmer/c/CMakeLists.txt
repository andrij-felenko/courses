# Скрипт збірки проєкту прошивки DAPLink мовою C через CMake
cmake_minimum_required(VERSION 3.16)

# Оголошення крос-компіляційного проєкту для мікроконтролерів ARM Cortex-M
project(daplink_firmware C ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Прапорці компілятора під архітектуру ARM Cortex-M3 (STM32F103)
add_compile_options(
    -mcpu=cortex-m3
    -mthumb
    -Wall
    -Wextra
    -ffunction-sections
    -fdata-sections
    -O2
)

# Каталоги заголовочних файлів проєкту (HIC Layer, Board Layer, CMSIS-DAP, RTOS)
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/cmsis_dap
    ${CMAKE_CURRENT_SOURCE_DIR}/rtos
)

# Вихідні файли проєкту
set(PROJECT_SOURCES
    daplink_board.c
    main.c
)

# Створення виконуваного файлу ELF
add_executable(${PROJECT_NAME}.elf ${PROJECT_SOURCES})

# Прапорці компонувальника та використання скрипту лінкувальника (Linker Script)
target_link_options(${PROJECT_NAME}.elf PRIVATE
    -mcpu=cortex-m3
    -mthumb
    -T${CMAKE_CURRENT_SOURCE_DIR}/stm32f103.ld
    -Wl,--gc-sections
    -Wl,-Map=${PROJECT_NAME}.map
)

# Автоматична генерація підсумкових бінарних образів .bin та .hex для прошивки
add_custom_command(TARGET ${PROJECT_NAME}.elf POST_BUILD
    COMMAND arm-none-eabi-objcopy -O binary ${PROJECT_NAME}.elf ${PROJECT_NAME}.bin
    COMMAND arm-none-eabi-objcopy -O ihex ${PROJECT_NAME}.elf ${PROJECT_NAME}.hex
    COMMENT "Генерація бінарних файлів прошивки DAPLink (.bin / .hex)"
)
