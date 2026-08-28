cmake_minimum_required(VERSION 3.20)
project(CantorGenerator VERSION 1.0.0 LANGUAGES C CXX)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(OpenMP REQUIRED)

add_executable(cantor_demo 
    proj-cantor-generator.c
    main.cpp
)

target_link_libraries(cantor_demo PRIVATE OpenMP::OpenMP_CXX)
target_compile_options(cantor_demo PRIVATE 
    $<$<CXX_COMPILER_ID:GNU>:-O3 -march=native -ffast-math>
    $<$<CXX_COMPILER_ID:Clang>:-O3 -march=native -ffast-math>
    $<$<CXX_COMPILER_ID:MSVC>:/O2 /arch:AVX2>
)
