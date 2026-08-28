if(CMAKE_CROSSCOMPILING)
    find_program(HOST_TABLE_GEN table_gen REQUIRED)
    add_executable(table_gen IMPORTED GLOBAL)
    set_target_properties(table_gen PROPERTIES
        IMPORTED_LOCATION "${HOST_TABLE_GEN}"
    )
else()
    add_executable(table_gen tools/table_gen.cpp)
endif()

add_custom_command(
    OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/sin_tables.c"
    COMMAND table_gen "${CMAKE_CURRENT_BINARY_DIR}/sin_tables.c"
    DEPENDS table_gen
    VERBATIM
)
