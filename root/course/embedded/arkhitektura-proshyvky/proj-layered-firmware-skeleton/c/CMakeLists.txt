cmake_minimum_required(VERSION 3.16)
project(firmware_skeleton C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Шари, які не знають про платформу, — одні й ті самі байти для чипа й для хоста.
add_library(firmware_core
    hal/hal_i2c.h
    hal/hal_gpio.h
    hal/hal_time.h
    hal/hal_critical.h
    bsp/bsp_bme280.c
    bsp/bsp_power.c
    services/event_queue.c
    services/event_dispatcher.c
    services/power_manager.c
    app/app_telemetry.c
)
target_include_directories(firmware_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_compile_options(firmware_core PRIVATE -Wall -Wextra -Wconversion
                       # Кожна функція і таблиця — в окрему секцію, щоб компонувальник
                       # викинув з прошивки все, чого ця збірка не викликає.
                       -ffunction-sections -fdata-sections)

add_executable(host_test targets/host_test_main.c)
target_link_libraries(host_test PRIVATE firmware_core m)
target_link_options(host_test PRIVATE -Wl,--gc-sections)

enable_testing()
add_test(NAME firmware_skeleton COMMAND host_test)

# Прошивку для плати збирає окремий тулчейн-файл під arm-none-eabi:
# targets/stm32_target_main.c потребує вендорного CMSIS-пакета STM32F4.
