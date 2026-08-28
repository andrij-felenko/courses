cmake_minimum_required(VERSION 3.28)
project(ExternalConsumer CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Пошук встановленої модульної бібліотеки
find_package(MatrixLib REQUIRED CONFIG)

add_executable(consumer_app consumer_main.cpp)

# Підключення автоматично імпортує вихідні інтерфейси модулів у дерево збірки споживача
target_link_libraries(consumer_app PRIVATE math::matrix_lib)
