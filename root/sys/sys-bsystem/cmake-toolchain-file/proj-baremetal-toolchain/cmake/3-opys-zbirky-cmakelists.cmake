cmake_minimum_required(VERSION 3.20)
project(stm32_firmware C CXX ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 1. Інтерфейсна ціль для прапорців архітектури Cortex-M4 з апаратним FPU
add_library(cortex_m4_flags INTERFACE)
target_compile_options(cortex_m4_flags INTERFACE
    -mcpu=cortex-m4
    -mthumb
    -mfpu=fpv4-sp-d16
    -mfloat-abi=hard
    -ffunction-sections
    -fdata-sections
    -Wall
    -Wextra
)

target_link_options(cortex_m4_flags INTERFACE
    -mcpu=cortex-m4
    -mthumb
    -mfpu=fpv4-sp-d16
    -mfloat-abi=hard
    -T${CMAKE_CURRENT_SOURCE_DIR}/linker.ld
    -Wl,--gc-sections
    --specs=nano.specs
    --specs=nosys.specs
    -Wl,-Map=${CMAKE_CURRENT_BINARY_DIR}/firmware.map
)

# 2. Виконуваний файл прошивки
add_executable(firmware.elf
    startup.c
    main.cpp
)

target_link_libraries(firmware.elf PRIVATE cortex_m4_flags)

# 3. Генерація файлів образів пам'яті для програматора (.hex та .bin)
add_custom_command(TARGET firmware.elf POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} -O ihex $<TARGET_FILE:firmware.elf> ${CMAKE_CURRENT_BINARY_DIR}/firmware.hex
    COMMAND ${CMAKE_OBJCOPY} -O binary $<TARGET_FILE:firmware.elf> ${CMAKE_CURRENT_BINARY_DIR}/firmware.bin
    COMMAND ${CMAKE_SIZE} $<TARGET_FILE:firmware.elf>
    COMMENT "Створення бінарних файлів .hex і .bin та вивід розміру секцій:"
)
