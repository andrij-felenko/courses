# CMakeLists.txt (C та C++)
add_executable(firmware.elf
    src/main.c
    src/sensors.c
    src/startup_stm32f401xe.s
)

target_link_options(firmware.elf PRIVATE
    -T${CMAKE_CURRENT_SOURCE_DIR}/linker/STM32F401RETx_FLASH.ld
    -Wl,-Map=${CMAKE_CURRENT_BINARY_DIR}/firmware.map
    -Wl,--cref
    -Wl,--gc-sections
    -Wl,--print-memory-usage
)
