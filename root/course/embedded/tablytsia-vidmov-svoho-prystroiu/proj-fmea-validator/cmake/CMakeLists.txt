# Інтеграція генерації реєстру відмов у CMake
find_package(Python3 REQUIRED COMPONENTS Interpreter)

add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/fmea_registry_autogen.h
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/scripts/fmea_validator.py
            ${CMAKE_CURRENT_SOURCE_DIR}/docs/fmea_matrix.json
            --out-dir ${CMAKE_CURRENT_BINARY_DIR}
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/docs/fmea_matrix.json
            ${CMAKE_CURRENT_SOURCE_DIR}/scripts/fmea_validator.py
    COMMENT "Валідація матриці FMEA та генерація C-заголовків реєстру відмов"
)

add_custom_target(generate_fmea_registry ALL
    DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/fmea_registry_autogen.h
)
