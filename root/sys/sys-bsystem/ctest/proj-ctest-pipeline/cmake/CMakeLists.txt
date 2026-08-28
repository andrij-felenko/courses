cmake_minimum_required(VERSION 3.24)
project(EngineTests LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Опція збірки з адресним санітайзером та перевіркою UB
option(ENABLE_ASAN "Увімкнути AddressSanitizer та UndefinedBehaviorSanitizer" OFF)

if(ENABLE_ASAN)
    if(CMAKE_CXX_COMPILER_ID MATCHES "Clang|GNU")
        add_compile_options(-fsanitize=address,undefined -fno-omit-frame-pointer -g)
        add_link_options(-fsanitize=address,undefined)
    endif()
endif()

# 1. Основна ціль бібліотеки
add_library(calc_engine STATIC src/calculator.cpp)
target_include_directories(calc_engine PUBLIC src)

# 2. Активація CTest у корені проєкту
include(CTest) # або enable_testing()

if(BUILD_TESTING)
    # Підключення GoogleTest через FetchContent
    include(FetchContent)
    FetchContent_Declare(
        googletest
        URL https://github.com/google/googletest/archive/refs/tags/v1.14.0.zip
    )
    # Забороняємо GTest встановлювати свої заголовки у системні каталоги
    set(INSTALL_GTEST OFF CACHE BOOL "" FORCE)
    FetchContent_MakeAvailable(googletest)

    include(GoogleTest)

    # ── Модульні тести (GoogleTest) ──────────────────────────────────────────
    add_executable(unit_tests tests/unit/test_calculator.cpp)
    target_link_libraries(unit_tests PRIVATE calc_engine GTest::gtest_main)

    # Динамічне опитування тестів після компіляції бінарника
    gtest_discover_tests(unit_tests
        PROPERTIES
            LABELS "unit"
            TIMEOUT 10
    )

    # ── Інтеграційні тести з декларативними фікстурами ────────────────────────
    add_executable(db_fixture_runner tests/integration/db_fixture.cpp)
    add_executable(storage_tests tests/integration/test_storage.cpp)
    target_link_libraries(storage_tests PRIVATE calc_engine)

    # Реєстрація етапу підготовки: створення тимчасової бази даних
    add_test(NAME db_setup
        COMMAND db_fixture_runner --setup "$<TARGET_FILE_DIR:storage_tests>/temp_db.dat"
    )
    set_tests_properties(db_setup PROPERTIES
        FIXTURES_SETUP "DatabaseFixture"
        LABELS "integration"
        TIMEOUT 15
    )

    # Реєстрація основного інтеграційного тесту, що читає створену БД
    add_test(NAME test_storage_read_write
        COMMAND storage_tests "$<TARGET_FILE_DIR:storage_tests>/temp_db.dat"
    )
    set_tests_properties(test_storage_read_write PROPERTIES
        FIXTURES_REQUIRED "DatabaseFixture"
        LABELS "integration"
        TIMEOUT 30
        COST 25.0
    )

    # Реєстрація обов'язкового очищення: видалення файлу БД навіть при аварії
    add_test(NAME db_cleanup
        COMMAND db_fixture_runner --cleanup "$<TARGET_FILE_DIR:storage_tests>/temp_db.dat"
    )
    set_tests_properties(db_cleanup PROPERTIES
        FIXTURES_CLEANUP "DatabaseFixture"
        LABELS "integration"
    )
endif()
