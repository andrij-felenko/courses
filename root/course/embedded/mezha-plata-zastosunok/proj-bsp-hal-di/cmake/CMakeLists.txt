# CMakeLists.txt — дві збірки з однієї кодової бази:
#   крос-компіляція  -> прошивка для STM32 (драйвер плати + main)
#   нативна збірка   -> модульні тести на хості (мок замість плати)
#
# Збирати звідси: cmake -B build_host -S .
cmake_minimum_required(VERSION 3.22)
project(BspHalDi C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 23)          # std::expected
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(SRC_C   ${CMAKE_CURRENT_SOURCE_DIR}/../c)
set(SRC_CXX ${CMAKE_CURRENT_SOURCE_DIR}/../cpp)

# Спільне ядро: переносна логіка, однакова для прошивки й для тестів.
add_library(app_core_c STATIC ${SRC_C}/supervisor.c)
target_include_directories(app_core_c PUBLIC ${SRC_C})

add_library(app_core_cxx STATIC ${SRC_CXX}/supervisor.cpp)
target_include_directories(app_core_cxx PUBLIC ${SRC_CXX})

if(CMAKE_CROSSCOMPILING)
    # Ціль ARM: до ядра приєднується реалізація плати.
    # Ціль stm32_hal приносить згенерований CubeMX проєкт (HAL, startup, linker script).
    add_executable(firmware_c.elf ${SRC_C}/main.c ${SRC_C}/bsp_target_stm32.c)
    target_link_libraries(firmware_c.elf PRIVATE app_core_c stm32_hal)

    add_executable(firmware_cxx.elf ${SRC_CXX}/main.cpp ${SRC_CXX}/stm32_board.cpp)
    target_link_libraries(firmware_cxx.elf PRIVATE app_core_cxx stm32_hal)
else()
    # Хост: до того самого ядра приєднується мок.
    enable_testing()

    add_executable(unit_tests_c ${SRC_C}/test_supervisor_host.c)
    target_link_libraries(unit_tests_c PRIVATE app_core_c)
    add_test(NAME SupervisorTestsC COMMAND unit_tests_c)

    add_executable(unit_tests_cxx ${SRC_CXX}/test_supervisor_host.cpp)
    target_link_libraries(unit_tests_cxx PRIVATE app_core_cxx)
    add_test(NAME SupervisorTestsCxx COMMAND unit_tests_cxx)

    # На хості тести безкоштовно їдуть під санітайзером — на МК такої розкоші немає.
    if(NOT MSVC)
        foreach(target unit_tests_c unit_tests_cxx app_core_c app_core_cxx)
            target_compile_options(${target} PRIVATE -Wall -Wextra -g -fsanitize=address,undefined)
            target_link_options(${target} PRIVATE -fsanitize=address,undefined)
        endforeach()
    endif()
endif()
