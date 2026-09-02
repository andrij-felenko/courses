cmake_minimum_required(VERSION 3.20)
project(bumpless_pid_demo CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(bumpless_pid
    src/bumpless_pid.cpp
    src/plant.cpp
)
target_include_directories(bumpless_pid PUBLIC include)
target_compile_options(bumpless_pid PRIVATE -Wall -Wextra -Wpedantic)

add_executable(bumpless_demo src/main.cpp)
target_link_libraries(bumpless_demo PRIVATE bumpless_pid)
