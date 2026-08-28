add_executable(parser_test tests/test_parser.cpp)
target_link_libraries(parser_test PRIVATE core_engine)

add_test(NAME verify_json_parser
    COMMAND parser_test
            --input "$<TARGET_PROPERTY:core_engine,SOURCE_DIR>/testdata/valid.json"
            --schema "$<TARGET_FILE:schema_validator>"
            --log-level "$<IF:$<CONFIG:Debug>,verbose,error>"
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
)
