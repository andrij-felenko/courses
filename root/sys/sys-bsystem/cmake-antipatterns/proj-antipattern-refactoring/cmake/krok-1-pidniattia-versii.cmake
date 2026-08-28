cmake_minimum_required(VERSION 3.20...3.30)
project(ImageProcessor 
    VERSION 1.2.0 
    LANGUAGES CXX
    DESCRIPTION "Сучасна бібліотека обробки зображень"
)

# Апаратне блокування in-source збірки
if(CMAKE_SOURCE_DIR STREQUAL CMAKE_BINARY_DIR)
    message(FATAL_ERROR 
        "❌ In-source збірка суворо заборонена!\n"
        "CMake згенерував службові файли всередині дерева сирців.\n"
        "Створіть окремий каталог: cmake -B build"
    )
endif()
