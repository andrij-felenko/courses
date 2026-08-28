cmake_minimum_required(VERSION 3.20)
project(cms_sign_verify C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(OpenSSL 3.0 REQUIRED)

# Збірка C версії
add_executable(cms_tool_c main.c)
target_link_libraries(cms_tool_c PRIVATE OpenSSL::Crypto OpenSSL::SSL)
target_compile_options(cms_tool_c PRIVATE -Wall -Wextra -Wpedantic -Werror)

# Збірка C++23 версії
add_executable(cms_tool_cpp main.cpp)
target_link_libraries(cms_tool_cpp PRIVATE OpenSSL::Crypto OpenSSL::SSL)
target_compile_options(cms_tool_cpp PRIVATE -Wall -Wextra -Wpedantic -Werror)
