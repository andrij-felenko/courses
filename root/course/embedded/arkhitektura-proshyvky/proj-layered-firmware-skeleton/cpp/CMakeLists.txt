cmake_minimum_required(VERSION 3.16)
project(firmware_skeleton CXX)

set(CMAKE_CXX_STANDARD 23)  # std::expected, std::span, std::print
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Шари, які не знають про платформу, — одні й ті самі байти для чипа й для хоста.
add_library(firmware_core
    bsp/bsp_bme280.cpp
    bsp/power_rail.cpp
    services/power_manager.cpp
    app/app_telemetry.cpp
)
target_include_directories(firmware_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_compile_options(firmware_core PRIVATE -Wall -Wextra
                       # Кожна функція і таблиця віртуальних методів — в окрему секцію,
                       # щоб компонувальник викинув з прошивки все невикористане.
                       -ffunction-sections -fdata-sections)

add_executable(host_test targets/host_test_main.cpp)
target_link_libraries(host_test PRIVATE firmware_core)
target_link_options(host_test PRIVATE -Wl,--gc-sections)

enable_testing()
add_test(NAME firmware_skeleton COMMAND host_test)

# Прошивку для плати збирає окремий тулчейн-файл під arm-none-eabi:
# targets/stm32_target_main.cpp потребує вендорного CMSIS-пакета STM32F4.
