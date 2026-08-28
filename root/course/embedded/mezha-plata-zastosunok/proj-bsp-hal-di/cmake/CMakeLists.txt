# CMakeLists.txt: Подвійна збірка (Target Firmware vs Host Unit Tests)
cmake_minimum_required(VERSION 3.22)
project(FirmwareProject C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 23)

# Спільне ядро бізнес-логіки (100% переносний код)
add_library(app_core STATIC
    supervisor.c
)
target_include_directories(app_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

# 1. Якщо компілюємо під цільовий мікроконтролер ARM
if(CMAKE_CROSSCOMPILING)
    add_executable(firmware.elf
        main.c
        bsp_target_stm32.c
    )
    target_link_libraries(firmware.elf PRIVATE app_core stm32_hal)
else()
    # 2. Якщо компілюємо під хостовий ПК для CI/CD
    enable_testing()
    add_executable(unit_tests
        test_supervisor_host.c
    )
    target_link_libraries(unit_tests PRIVATE app_core)
    add_test(NAME SupervisorTests COMMAND unit_tests)
endif()
