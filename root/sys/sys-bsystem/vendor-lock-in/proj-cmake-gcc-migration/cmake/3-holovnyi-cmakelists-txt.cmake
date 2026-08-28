cmake_minimum_required(VERSION 3.22)

# Автоматичне підключення тулчейну, якщо не передано через CLI
if(NOT CMAKE_TOOLCHAIN_FILE)
    set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_SOURCE_DIR}/cmake/toolchain-arm-none-eabi.cmake")
endif()

project(firmware-portable C CXX ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(${PROJECT_NAME}.elf
    core/src/main.cpp
    core/src/startup_stm32f407xx.c
    core/src/syscalls.c
    core/src/system_stm32f4xx.c
    drivers/src/uart_driver.cpp
)

target_include_directories(${PROJECT_NAME}.elf PRIVATE
    core/inc
    drivers/inc
    drivers/cmsis/inc
)

# Передача скрипта компонувальника
set(LINKER_SCRIPT "${CMAKE_CURRENT_SOURCE_DIR}/linker/STM32F407VGTx_FLASH.ld")
target_link_options(${PROJECT_NAME}.elf PRIVATE
    -T${LINKER_SCRIPT}
    -Wl,-Map=${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}.map,--cref
)

# Генерація сирих бінарних файлів та виведення розміру секцій
add_custom_command(TARGET ${PROJECT_NAME}.elf POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} -O ihex ${PROJECT_NAME}.elf ${PROJECT_NAME}.hex
    COMMAND ${CMAKE_OBJCOPY} -O binary ${PROJECT_NAME}.elf ${PROJECT_NAME}.bin
    COMMAND ${CMAKE_SIZE} --format=berkeley ${PROJECT_NAME}.elf
    COMMENT "Generating raw binaries (.hex, .bin) and calculating memory footprint"
)
