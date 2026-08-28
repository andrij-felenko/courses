cmake_minimum_required(VERSION 3.20)
project(telemetry_daemon LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(telemetry REQUIRED)
find_package(fmt REQUIRED)
find_package(nlohmann_json REQUIRED)

add_executable(telemetry_daemon main.cpp)
target_link_libraries(telemetry_daemon PRIVATE
    telemetry::telemetry
    fmt::fmt
    nlohmann_json::nlohmann_json
)
