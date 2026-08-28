cmake_minimum_required(VERSION 3.24)
project(telemetry_service CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(fast-telemetry CONFIG REQUIRED)
find_package(fmt CONFIG REQUIRED)

add_executable(telemetry_service src/main.cpp)
target_link_libraries(telemetry_service PRIVATE fast-telemetry::fast-telemetry fmt::fmt)
