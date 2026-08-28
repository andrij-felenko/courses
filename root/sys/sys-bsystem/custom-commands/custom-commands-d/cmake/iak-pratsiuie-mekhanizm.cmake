add_custom_command(
    OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/protocol.cpp"
    COMMAND dsl_compiler --input "${CMAKE_CURRENT_SOURCE_DIR}/dsl/api.dsl"
                         --output "${CMAKE_CURRENT_BINARY_DIR}/protocol.cpp"
                         --depfile "${CMAKE_CURRENT_BINARY_DIR}/protocol.cpp.d"
    DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/dsl/api.dsl"
    DEPFILE "${CMAKE_CURRENT_BINARY_DIR}/protocol.cpp.d"
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
    COMMENT "Компіляція схеми api.dsl з відстеженням імпортів"
    VERBATIM
)
