cmake_minimum_required(VERSION 3.20)
project(OscillatorSimulation LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Пошук встановленої бібліотеки libbm_averaging
find_package(libbm_averaging REQUIRED)

add_executable(sim_main main.cpp)
target_link_libraries(sim_main PRIVATE libbm_averaging::bm_averaging)
