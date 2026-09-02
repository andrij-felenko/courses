cmake_minimum_required(VERSION 3.16)
project(bumpless_transfer C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

add_executable(bumpless
    src/main.c
    src/bumpless_pid.c
    src/ramp.c
    src/plant.c
    src/cascade.c
    src/portable_irq.c
    src/hil.c
)

target_include_directories(bumpless PRIVATE include)

if(NOT MSVC)
    target_compile_options(bumpless PRIVATE -Wall -Wextra)
endif()

if(UNIX)
    target_link_libraries(bumpless PRIVATE m)
endif()
