# CMakeLists.txt
cmake_minimum_required(VERSION 3.20)
project(FeatureDetectionProject CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include(CheckCXXSourceCompiles)

# Перевірка реальної наявності працездатного std::format у середовищі
check_cxx_source_compiles("
    #include <format>
    #include <string>
    int main() {
        std::string s = std::format(\"Test: {}\", 42);
        return s.empty() ? 1 : 0;
    }
" HAVE_STD_FORMAT)

add_executable(app main.cpp)

if(HAVE_STD_FORMAT)
    target_compile_definitions(app PRIVATE HAS_STD_FORMAT=1)
    message(STATUS "Native std::format is available and functional")
else()
    target_compile_definitions(app PRIVATE HAS_STD_FORMAT=0)
    message(STATUS "Native std::format is missing; linking external fmt library fallback")
    # find_package(fmt REQUIRED)
    # target_link_libraries(app PRIVATE fmt::fmt)
endif()

# Налаштування суворої діагностики
if(MSVC)
    target_compile_options(app PRIVATE /W4 /WX /permissive- /Zc:__cplusplus /Zc:preprocessor)
else()
    target_compile_options(app PRIVATE -Wall -Wextra -Wpedantic -Werror)
endif()
