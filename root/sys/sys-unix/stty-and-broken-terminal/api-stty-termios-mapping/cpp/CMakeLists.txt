cmake_minimum_required(VERSION 3.25)
project(ttyxx CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(ttyxx
    src/main.cpp
    src/flags.cpp
    src/terminal.cpp
    src/pty_session.cpp
    src/abi.cpp
    src/baud.cpp)

target_compile_options(ttyxx PRIVATE -Wall -Wextra)
