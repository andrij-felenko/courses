cmake_minimum_required(VERSION 3.14)
project(sht30_climate_monitor CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(include)

add_executable(sht30_demo
    src/main.cpp
    src/sht30.cpp
    src/climate_monitor.cpp
)
