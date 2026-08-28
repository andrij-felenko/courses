cmake_minimum_required(VERSION 3.20)
project(EventFilterModule VERSION 2.4.0 LANGUAGES C CXX)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Прапорці суворої перевірки якості коду
if (MSVC)
    add_compile_options(/W4 /WX)
else()
    add_compile_options(-Wall -Wextra -Wpedantic -Werror -Wconversion -Wshadow)
endif()

# Статична бібліотека фільтра
add_library(event_filter STATIC
    src/event_filter.c
)
target_include_directories(event_filter PUBLIC include)

# Випробувальний стенд C99
add_executable(test_event_filter_c tests/test_event_filter.c)
target_link_libraries(test_event_filter_c PRIVATE event_filter)

# Випробувальний стенд C++20
add_executable(test_event_filter_cpp tests/test_event_filter.cpp)
target_include_directories(test_event_filter_cpp PRIVATE include)

enable_testing()
add_test(NAME C99_Unit_And_MonteCarlo_Tests COMMAND test_event_filter_c)
add_test(NAME CXX20_Modern_Template_Tests COMMAND test_event_filter_cpp)
