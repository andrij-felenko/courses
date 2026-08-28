cmake_minimum_required(VERSION 3.20)
project(TelemetryPipeline LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 1. Визначення виконуваного файлу генератора
if(CMAKE_CROSSCOMPILING)
    find_program(HOST_DSL_COMPILER dsl_compiler REQUIRED)
    set(COMPILER_BIN "${HOST_DSL_COMPILER}")
    set(COMPILER_TARGET_DEP "")
else()
    add_executable(dsl_compiler tools/dsl_compiler.cpp)
    set(COMPILER_BIN "$<TARGET_FILE:dsl_compiler>")
    set(COMPILER_TARGET_DEP dsl_compiler)
endif()

# 2. Шляхи до артефактів у дереві бінарників
set(GEN_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated")
set(GEN_HEADER "${GEN_DIR}/messages.hpp")
set(GEN_SOURCE "${GEN_DIR}/messages.cpp")
set(GEN_DEPFILE "${GEN_DIR}/messages.cpp.d")
set(DSL_INPUT "${CMAKE_CURRENT_SOURCE_DIR}/dsl/messages.dsl")

# 3. Власна команда генерації з підтримкою DEPFILE
add_custom_command(
    OUTPUT "${GEN_HEADER}" "${GEN_SOURCE}"
    COMMAND ${COMPILER_BIN}
            --input "${DSL_INPUT}"
            --out-dir "${GEN_DIR}"
            --depfile "${GEN_DEPFILE}"
    DEPENDS "${DSL_INPUT}" ${COMPILER_TARGET_DEP}
    DEPFILE "${GEN_DEPFILE}"
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
    COMMENT "Генерація коду телеметрії з ${DSL_INPUT}"
    VERBATIM
    COMMAND_EXPAND_LISTS
)

# 4. Створення цільової програми
add_executable(firmware_app src/main.cpp)

# 5. Підключення згенерованих файлів до програми
target_sources(firmware_app PRIVATE "${GEN_SOURCE}" "${GEN_HEADER}")
target_include_directories(firmware_app PRIVATE "${GEN_DIR}")
