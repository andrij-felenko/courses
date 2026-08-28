cmake_minimum_required(VERSION 3.20)
project(ionopath C CXX)

set(CMAKE_C_STANDARD 99)
set(CMAKE_CXX_STANDARD 20)

add_library(ionopath_c calculate_iono.c)
add_library(ionopath_cpp IonosphereCalculator.cpp)

add_executable(iono_calc_cli main.cpp)
target_link_libraries(iono_calc_cli PRIVATE ionopath_cpp)
