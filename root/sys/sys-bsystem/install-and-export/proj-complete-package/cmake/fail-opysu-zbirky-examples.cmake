cmake_minimum_required(VERSION 3.20)
project(ConsumerApp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Пошук встановленої бібліотеки в режимі конфігурації
find_package(Hyperion 1.2 REQUIRED CONFIG)

add_executable(consumer_app main.cpp)

# Лінкування з імпортованими цілями простору імен Hyperion::
target_link_libraries(consumer_app
    PRIVATE
        Hyperion::core
        Hyperion::math
)
