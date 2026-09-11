cmake_minimum_required(VERSION 3.20)
project(boundary_cost_benchmarks LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Налаштування компілятора для оптимізації та строгих попереджень
if(MSVC)
    add_compile_options(/O2 /W4 /permissive-)
    add_definitions(-D_CRT_SECURE_NO_WARNINGS)
else()
    add_compile_options(-O3 -Wall -Wextra -Wpedantic)
endif()

# Пошук бібліотеки потоків
find_package(Threads REQUIRED)

# Пошук Google Benchmark та nlohmann_json
find_package(benchmark CONFIG QUIET)
find_package(nlohmann_json CONFIG QUIET)

# Якщо пакунки не встановлені в системі, завантажуємо їх через FetchContent
if(NOT benchmark_FOUND OR NOT nlohmann_json_FOUND)
    include(FetchContent)
    if(NOT benchmark_FOUND)
        FetchContent_Declare(
            benchmark
            GIT_REPOSITORY https://github.com/google/benchmark.git
            GIT_TAG v1.8.3
        )
        set(BENCHMARK_ENABLE_TESTING OFF CACHE BOOL "" FORCE)
        set(BENCHMARK_ENABLE_INSTALL OFF CACHE BOOL "" FORCE)
        FetchContent_MakeAvailable(benchmark)
    endif()
    if(NOT nlohmann_json_FOUND)
        FetchContent_Declare(
            nlohmann_json
            GIT_REPOSITORY https://github.com/nlohmann/json.git
            GIT_TAG v3.11.3
        )
        FetchContent_MakeAvailable(nlohmann_json)
    endif()
endif()

# Головний виконуваний файл стенда бенчмаркінгу
add_executable(boundary_benchmarks
    src/main.cpp
    src/in_process_benchmarks.cpp
    src/ipc_benchmarks.cpp
    src/rpc_benchmarks.cpp
)

target_include_directories(boundary_benchmarks PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_link_libraries(boundary_benchmarks PRIVATE
    benchmark::benchmark
    nlohmann_json::nlohmann_json
    Threads::Threads
)

if(WIN32)
    target_link_libraries(boundary_benchmarks PRIVATE ws2_32)
endif()
