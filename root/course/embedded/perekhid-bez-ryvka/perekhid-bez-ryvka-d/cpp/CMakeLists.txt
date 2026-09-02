cmake_minimum_required(VERSION 3.16)
project(bumpless_transfer CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(bumpless
    src/main.cpp
    src/pid.cpp
    src/ramp.cpp
    src/plant.cpp
    src/cascade.cpp
    src/hil.cpp
)

target_include_directories(bumpless PRIVATE include)

if(NOT MSVC)
    target_compile_options(bumpless PRIVATE -Wall -Wextra)
endif()
