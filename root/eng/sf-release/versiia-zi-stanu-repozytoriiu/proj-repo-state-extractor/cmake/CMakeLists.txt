# CMakeLists.txt
cmake_minimum_required(VERSION 3.20)
project(FirmwareApp C CXX)

set(VERSION_HEADER_PATH "${CMAKE_CURRENT_BINARY_DIR}/generated/version_info.h")
set(VERSION_SOURCE_PATH "${CMAKE_CURRENT_BINARY_DIR}/generated/version_info.c")

# Визначення, чи активний релізний режим
set(IS_RELEASE_BUILD FALSE)
if(CMAKE_BUILD_TYPE STREQUAL "Release" OR CMAKE_BUILD_TYPE STREQUAL "MinSizeRel")
    set(IS_RELEASE_BUILD TRUE)
endif()

add_custom_target(generate_version_metadata
    COMMAND ${Python3_EXECUTABLE} "${CMAKE_CURRENT_SOURCE_DIR}/scripts/gen_version.py"
            --output-header "${VERSION_HEADER_PATH}"
            --output-source "${VERSION_SOURCE_PATH}"
            $<$<BOOL:${IS_RELEASE_BUILD}>:--fail-on-dirty>
    BYPRODUCTS "${VERSION_HEADER_PATH}" "${VERSION_SOURCE_PATH}"
    COMMENT "Перевірка стану Git-репозиторію та генерація метаданих версії..."
)

add_executable(firmware_app
    src/main.c
    src/driver.c
    "${VERSION_SOURCE_PATH}"
)

add_dependencies(firmware_app generate_version_metadata)
target_include_directories(firmware_app PRIVATE "${CMAKE_CURRENT_BINARY_DIR}/generated")
