cmake_minimum_required(VERSION 3.20)

# Оголошення проєкту прошивки програматора DAPLink
project(daplink_firmware C CXX ASM)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Налаштування інструментарію крос-компіляції ARM GCC
set(ARM_TARGET_TRIPLE "arm-none-eabi")
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR arm)

# Прапорці компілятора під процесорне ядро ARM Cortex-M4
add_compile_options(
    -mcpu=cortex-m4
    -mthumb
    -mfpu=fpv4-sp-d16
    -mfloat-abi=hard
    -Wall
    -Wextra
    -ffunction-sections
    -fdata-sections
    -fno-exceptions
    -fno-rtti
)

# Визначення директорій з заголовочними файлами
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/cmsis_dap
    ${CMAKE_CURRENT_SOURCE_DIR}/rtos
    ${CMAKE_CURRENT_SOURCE_DIR}/usb_stack
)

# Вихідні файли проєкту апаратного шару плати
set(BOARD_SOURCES
    src/target_board.cpp
)

# Створення виконуваного ELF-файлу
add_executable(${PROJECT_NAME}.elf ${BOARD_SOURCES})

# Прапорці лінкеру з посиланням на скрипт компанування (Linker Script)
target_link_options(${PROJECT_NAME}.elf PRIVATE
    -mcpu=cortex-m4
    -mthumb
    -mfpu=fpv4-sp-d16
    -mfloat-abi=hard
    -T${CMAKE_CURRENT_SOURCE_DIR}/stm32f401xc.ld
    -Wl,--gc-sections
    -Wl,-Map=${PROJECT_NAME}.map
    --specs=nano.specs
)

# Ґенерація підсумкових двійкових форматів прошивки .bin та .hex
add_custom_command(TARGET ${PROJECT_NAME}.elf POST_BUILD
    COMMAND arm-none-eabi-objcopy -O binary ${PROJECT_NAME}.elf ${PROJECT_NAME}.bin
    COMMAND arm-none-eabi-objcopy -O ihex ${PROJECT_NAME}.elf ${PROJECT_NAME}.hex
    COMMENT "Building binary and hex images for DAPLink target..."
)
