# 1. Тест підготовки: створення БД та наповнення таблиць
add_test(NAME setup_test_database
    COMMAND test_db_manager --create-database "temp_test_db"
)
set_tests_properties(setup_test_database PROPERTIES
    FIXTURES_SETUP "DatabaseFixture"
    TIMEOUT 20.0
)

# 2. Робочі тести, які читають і модифікують базу
add_test(NAME test_user_authentication
    COMMAND auth_service_test --db "temp_test_db"
)
add_test(NAME test_order_processing
    COMMAND order_service_test --db "temp_test_db"
)
set_tests_properties(test_user_authentication test_order_processing PROPERTIES
    FIXTURES_REQUIRED "DatabaseFixture"
    TIMEOUT 10.0
)

# 3. Тест очищення: видалення файлів бази та зупинка демона
add_test(NAME cleanup_test_database
    COMMAND test_db_manager --drop-database "temp_test_db"
)
set_tests_properties(cleanup_test_database PROPERTIES
    FIXTURES_CLEANUP "DatabaseFixture"
)
