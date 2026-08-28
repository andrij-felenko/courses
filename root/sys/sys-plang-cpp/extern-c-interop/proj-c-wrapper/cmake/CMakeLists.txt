cmake_minimum_required(VERSION 3.20)
project(EngineCoreLibrary LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Глобальне приховування символів у Linux/macOS
set(CMAKE_CXX_VISIBILITY_PRESET hidden)
set(CMAKE_VISIBILITY_INLINES_HIDDEN ON)

# Створення динамічної бібліотеки
add_library(engine SHARED
    src/engine_api.cpp
)

# Визначення макроса ENGINE_EXPORTS під час компіляції самої бібліотеки
target_compile_definitions(engine PRIVATE ENGINE_EXPORTS)

target_include_directories(engine PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# Версіонування бібліотеки для Linux (soname)
set_target_properties(engine PROPERTIES
    VERSION 1.0.0
    SOVERSION 1
)
