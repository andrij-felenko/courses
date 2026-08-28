find_package(GTest REQUIRED)
include(GoogleTest)

add_executable(math_tests tests/test_math.cpp)
target_link_libraries(math_tests PRIVATE GTest::gtest_main)

# Динамічне виявлення тестів
gtest_discover_tests(math_tests
    EXTRA_ARGS "--custom_flag"
    PROPERTIES
        TIMEOUT 10.0
        LABELS "unit;math"
    DISCOVERY_TIMEOUT 30
    TEST_PREFIX "MathCore."
)
