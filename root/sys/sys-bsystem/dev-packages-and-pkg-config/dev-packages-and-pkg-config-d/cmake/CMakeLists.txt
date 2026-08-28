# CMakeLists.txt
cmake_minimum_required(VERSION 3.16)
project(ImageProcessor LANGUAGES C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 20)

# Завантаження модуля пошуку pkg-config
find_package(PkgConfig REQUIRED)

# Пошук бібліотеки libpng версії не менше 1.6
# Прапорець IMPORTED_TARGET створює повноцінну імпортовану ціль PkgConfig::PNG
pkg_check_modules(PNG REQUIRED IMPORTED_TARGET libpng>=1.6)

# Створення виконуваного файлу
add_executable(img_proc src/main.c)

# Прив'язка залежності через імпортовану ціль
target_link_libraries(img_proc PRIVATE PkgConfig::PNG)
