cmake_minimum_required(VERSION 3.20...3.30)
project(ImageProcessor
    VERSION 1.2.0
    LANGUAGES CXX
    DESCRIPTION "Бібліотека обробки зображень, побудована за канонами Modern CMake"
)

# 1. Захист від збирання у дереві сирців
if(CMAKE_SOURCE_DIR STREQUAL CMAKE_BINARY_DIR)
    message(FATAL_ERROR "Збірка всередині сирців заборонена! Використовуйте cmake -B build")
endif()

# 2. Опції конфігурації
option(IMGPROC_ENABLE_OPENMP "Увімкнути паралелізм OpenMP" ON)
option(IMGPROC_ENABLE_ASAN "Увімкнути AddressSanitizer" OFF)
option(BUILD_TESTING "Збирати юніт-тести" OFF)

# 3. Службові функції (замість макросів)
function(imgproc_add_filter_metadata target_name)
    set(temp_meta_dir "${CMAKE_CURRENT_BINARY_DIR}/meta_${target_name}")
    add_custom_target("${target_name}_metadata"
        COMMAND ${CMAKE_COMMAND} -E make_directory "${temp_meta_dir}"
        COMMENT "Генерація метаданих для ${target_name}"
        VERBATIM
    )
endfunction()

# 4. Основна ціль бібліотеки
add_library(imgproc STATIC
    src/filter.cpp
    src/internal_simd.cpp
)
add_library(ImageProcessor::imgproc ALIAS imgproc)

target_compile_features(imgproc PUBLIC cxx_std_17)

target_include_directories(imgproc
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_compile_definitions(imgproc
    PRIVATE
        IMGPROC_EXPORTS
)

target_compile_options(imgproc PRIVATE
    $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:AppleClang>,$<CXX_COMPILER_ID:GNU>>:
        -Wall -Wextra -Wpedantic
    >
    $<$<CXX_COMPILER_ID:MSVC>:
        /W4 /permissive-
    >
)

if(IMGPROC_ENABLE_ASAN)
    target_compile_options(imgproc PRIVATE
        $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:GNU>>:-fsanitize=address,undefined -fno-omit-frame-pointer>
    )
    target_link_options(imgproc PUBLIC
        $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:GNU>>:-fsanitize=address,undefined>
    )
endif()

if(IMGPROC_ENABLE_OPENMP)
    find_package(OpenMP REQUIRED)
    target_link_libraries(imgproc PUBLIC OpenMP::OpenMP_CXX)
endif()

imgproc_add_filter_metadata(imgproc)

# 5. Виконуваний файл додатку
add_executable(imgcli
    app/main.cpp
)

target_link_libraries(imgcli PRIVATE
    ImageProcessor::imgproc
)
