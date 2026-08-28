add_executable(crash_test tests/test_assertion_failure.cpp)

add_test(NAME expect_out_of_bounds_crash
    COMMAND crash_test --trigger-assert
)

set_tests_properties(expect_out_of_bounds_crash PROPERTIES
    WILL_FAIL TRUE
    TIMEOUT 5.0
)
