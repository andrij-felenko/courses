# Встановлення цільової архітектури та обмежень Freestanding
target_compile_options(firmware_target PRIVATE
    -mcpu=cortex-m4
    -mthumb
    -mfpu=fpv4-sp-d16
    -mfloat-abi=hard
    
    # Режим без операційної системи та вимкнення важких підсистем
    -ffreestanding
    -fno-exceptions
    -fno-rtti
    -fno-threadsafe-statics
    -fno-use-cxa-atexit
    -fno-unwind-tables
    -fno-asynchronous-unwind-tables
    
    # Оптимізація та секціонування для видалення мертвого коду
    -Os
    -ffunction-sections
    -fdata-sections
    -Wall
    -Wextra
    -Wpedantic
)

# Налаштування компонувальника
target_link_options(firmware_target PRIVATE
    -mcpu=cortex-m4
    -mthumb
    -mfpu=fpv4-sp-d16
    -mfloat-abi=hard
    -T${CMAKE_CURRENT_SOURCE_DIR}/linker_script.ld
    -Wl,--gc-sections
    -specs=nano.specs
    -specs=nosys.specs
    -Wl,-Map=${CMAKE_CURRENT_BINARY_DIR}/firmware.map
)
