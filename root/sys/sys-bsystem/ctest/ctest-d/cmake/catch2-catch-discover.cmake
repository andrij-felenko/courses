find_package(Catch2 3 REQUIRED)
include(Catch)

add_executable(network_tests tests/test_network.cpp)
target_link_libraries(network_tests PRIVATE Catch2::Catch2WithMain)

catch_discover_tests(network_tests
    PROPERTIES
        TIMEOUT 15.0
        LABELS "network"
)
