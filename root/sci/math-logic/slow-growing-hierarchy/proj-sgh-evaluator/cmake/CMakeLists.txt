cmake_minimum_required(VERSION 3.20)
project(SGHEngine C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)

add_library(sgh_c STATIC src/sgh_engine.c)
add_library(sgh_cpp STATIC src/sgh_engine.cpp)

add_executable(sgh-cli src/main.cpp)
target_link_libraries(sgh-cli PRIVATE sgh_cpp)
