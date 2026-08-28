// Приклад тестування конвеєра в Google Test
TEST(ConfigPipelineTest, HandlesFileNotFound) {
    auto result = load_service_configuration("non_existing_file.txt");
    
    // Перевіряємо, що результат містить помилку
    ASSERT_FALSE(result.has_value());
    EXPECT_EQ(result.error(), ConfigError::FileNotFound);
}

TEST(ConfigPipelineTest, ParsesValidConfig) {
    auto result = parse_config_raw("db.internal 5432 16");
    
    // Перевіряємо значення у разі успіху
    ASSERT_TRUE(result.has_value());
    EXPECT_EQ(result->db_host, "db.internal");
    EXPECT_EQ(result->port, 5432);
    EXPECT_EQ(result->worker_threads, 16);
}
