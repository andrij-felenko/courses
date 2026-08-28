cmake_minimum_required(VERSION 3.25)
project(libhorseshoe LANGUAGES C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(horseshoe STATIC horseshoe_c.c horseshoe.cpp)
