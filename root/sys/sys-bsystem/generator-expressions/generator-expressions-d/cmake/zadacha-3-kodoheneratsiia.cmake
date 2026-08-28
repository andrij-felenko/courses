# Створення цілі-інструмента
add_executable(schema_compiler tools/schema_compiler.cpp)

# Генерація файлу за допомогою скомпільованого інструмента
add_custom_command(
    OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/generated_schema.cpp"
           "${CMAKE_CURRENT_BINARY_DIR}/generated_schema.h"
    COMMAND $<TARGET_FILE:schema_compiler>
            --input "${CMAKE_CURRENT_SOURCE_DIR}/schema.json"
            --out-source "${CMAKE_CURRENT_BINARY_DIR}/generated_schema.cpp"
            --out-header "${CMAKE_CURRENT_BINARY_DIR}/generated_schema.h"
    DEPENDS schema_compiler "${CMAKE_CURRENT_SOURCE_DIR}/schema.json"
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
    COMMENT "Генерація коду моделі даних через schema_compiler"
    VERBATIM
)

# Основна програма, що споживає згенерований код
add_executable(app
    src/main.cpp
    "${CMAKE_CURRENT_BINARY_DIR}/generated_schema.cpp"
)

target_include_directories(app PRIVATE
    "${CMAKE_CURRENT_BINARY_DIR}"
)
