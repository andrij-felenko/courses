cmake_minimum_required(VERSION 3.20)
project(embedded_detector_metrics LANGUAGES C CXX)

set(CMAKE_C_STANDARD 99)
set(CMAKE_CXX_STANDARD 20)

# Прапорці оптимізації для вбудованих систем ARM
if(CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64")
    add_compile_options(-O3 -ffast-math -march=armv8-a+simd -flto)
elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "arm")
    add_compile_options(-O3 -mcpu=cortex-m7 -mfpu=fpv5-d16 -mfloat-abi=hard -flto)
else()
    add_compile_options(-O3 -march=native -flto)
endif()

add_library(detector_metrics_c STATIC src/detector_metrics.c)
add_library(detector_metrics_cpp STATIC src/detector_metrics.cpp)

add_executable(run_unit_tests tests/unit_tests.cpp)
target_link_libraries(run_unit_tests PRIVATE detector_metrics_cpp detector_metrics_c)
