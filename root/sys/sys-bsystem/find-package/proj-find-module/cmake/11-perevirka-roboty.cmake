# CMakeLists.txt
cmake_minimum_required(VERSION 3.20)
project(ImageCompressor LANGUAGES C CXX)

# Додаємо локальний каталог модулів до пошуку
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

# Знаходимо нашу бібліотеку
find_package(FastCodec 2.0 REQUIRED COMPONENTS PARALLEL)

# Створюємо ціль програми
add_executable(compress_tool src/main.cpp)

# Лінкуємо імпортовану ціль — заголовки, бібліотеки та макроси приходять автоматично
target_link_libraries(compress_tool PRIVATE FastCodec::FastCodec)
