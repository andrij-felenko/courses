cmake_minimum_required(VERSION 3.20)
project(ImageProcessor LANGUAGES CXX)

# Стандартні виклики пошуку пакетів Modern CMake
find_package(OpenSSL REQUIRED)
find_package(fmt REQUIRED)
find_package(zlib REQUIRED)

add_executable(image_processor src/main.cpp)

# Лінкування через безпечні імпортовані простори імен
target_link_libraries(image_processor PRIVATE
    OpenSSL::SSL
    OpenSSL::Crypto
    fmt::fmt
    ZLIB::ZLIB
)
