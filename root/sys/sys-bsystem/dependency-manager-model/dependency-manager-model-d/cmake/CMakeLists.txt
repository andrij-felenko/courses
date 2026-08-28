cmake_minimum_required(VERSION 3.20)
project(ImageProcessingService LANGUAGES CXX)

# Стандартний пошук конфігурації, згенерованої менеджером
find_package(fmt CONFIG REQUIRED)
find_package(PNG CONFIG REQUIRED)

add_executable(image_processor src/main.cpp src/filter.cpp)

# Імпортовані цілі самостійно передають усі шляхи, бібліотеки та дефайни
target_link_libraries(image_processor
    PRIVATE
        fmt::fmt
        PNG::PNG
)
