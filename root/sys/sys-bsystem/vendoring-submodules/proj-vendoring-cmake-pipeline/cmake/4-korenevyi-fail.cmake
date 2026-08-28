# Головний CMakeLists.txt
cmake_minimum_required(VERSION 3.20)
project(telemetry_service LANGUAGES C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Вмикаємо суворі прапорці якості коду для ВЛАСНИХ файлів проєкту
if(MSVC)
    add_compile_options(/W4 /WX)
else()
    add_compile_options(-Wall -Wextra -Wpedantic -Werror)
endif()

# Включаємо вендорений каталог
add_subdirectory(third_party)

# Головний бінарний виконуваний файл
add_executable(telemetry_node
    src/main.cpp
)

# Лінкуємося виключно до псевдонімів простору імен
target_link_libraries(telemetry_node
    PRIVATE
        Vendor::TinyXML2
        Vendor::Miniz
)
