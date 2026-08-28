# 1. Оголошення файлів результату генерації
set(GEN_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated")
set(GEN_SRC "${GEN_DIR}/protocol.cpp")
set(GEN_HDR "${GEN_DIR}/protocol.hpp")

# 2. Правило створення файлів
add_custom_command(
    OUTPUT "${GEN_SRC}" "${GEN_HDR}"
    COMMAND dsl_compiler --in "${CMAKE_CURRENT_SOURCE_DIR}/protocol.dsl"
                         --out-dir "${GEN_DIR}"
    DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/protocol.dsl"
    VERBATIM
)

# 3. Створення цільової бібліотеки
add_library(protocol_lib)

# 4. Приєднання згенерованих файлів до цілі
target_sources(protocol_lib
    PRIVATE
        "${GEN_SRC}"
        "${GEN_HDR}"
)

# 5. Надання доступу до згенерованих заголовків
target_include_directories(protocol_lib
    PUBLIC
        "$<BUILD_INTERFACE:${GEN_DIR}>"
)
