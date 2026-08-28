cmake_minimum_required(VERSION 3.20)
project(InstantiationProfilingDemo CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Прапорець для вмикання профілювання часу компіляції
option(ENABLE_TIME_TRACE "Enable compiler execution time tracing (-ftime-trace)" OFF)

if(ENABLE_TIME_TRACE)
    if(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
        add_compile_options(-ftime-trace)
        message(STATUS "Clang -ftime-trace enabled for compile time profiling.")
    elseif(CMAKE_CXX_COMPILER_ID MATCHES "GNU" AND CMAKE_CXX_COMPILER_VERSION VERSION_GREATER_EQUAL "14.0")
        add_compile_options(-ftime-trace)
        message(STATUS "GCC -ftime-trace enabled for compile time profiling.")
    else()
        message(WARNING "Time tracing option is not supported by current compiler.")
    endif()
endif()

# Додавання бібліотеки нешаблонної основи
add_library(buffer_base BufferBase.cpp)

# Додавання виконуваного модуля
add_executable(app_demo main.cpp)
target_link_libraries(app_demo PRIVATE buffer_base)
