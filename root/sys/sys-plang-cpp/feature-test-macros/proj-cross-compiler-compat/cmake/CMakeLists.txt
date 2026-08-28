cmake_minimum_required(VERSION 3.20)
project(CompatProject LANGUAGES CXX)

add_library(compat_core INTERFACE)
target_include_directories(compat_core INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/include)

# Бібліотека підтримує будь-який стандарт, починаючи з C++14
target_compile_features(compat_core INTERFACE cxx_std_14)

add_executable(telemetry_app main.cpp)
target_link_libraries(telemetry_app PRIVATE compat_core)
