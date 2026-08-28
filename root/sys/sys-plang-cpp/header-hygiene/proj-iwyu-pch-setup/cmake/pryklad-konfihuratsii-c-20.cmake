cmake_minimum_required(VERSION 3.28)
project(ModularApp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(network_module)

# Оголошення інтерфейсних файлів C++20 модулів
target_sources(network_module
    PUBLIC
        FILE_SET CXX_MODULES
        BASE_DIRS src/modules
        FILES
            src/modules/Network.ixx
            src/modules/Session.ixx
    PRIVATE
        src/modules/NetworkImpl.cpp
)

add_executable(app_modular src/main.cpp)
target_link_libraries(app_modular PRIVATE network_module)
