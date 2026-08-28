cmake_minimum_required(VERSION 3.20)
project(HostTools LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(table_gen table_gen.cpp)

# Встановлюємо виконуваний файл у каталог bin
install(TARGETS table_gen DESTINATION bin)
