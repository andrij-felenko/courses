void execute_query_pipeline(std::string_view query_sql) {
    auto* pool = get_thread_local_memory_resource();

    // PMR-вектор та PMR-рядок використовують локальну пам'ять потоку
    std::pmr::vector<std::pmr::string> tokens(pool);
    tokens.reserve(32);
    tokens.emplace_back("SELECT", pool);
    tokens.emplace_back("user_id", pool);
    tokens.emplace_back("FROM", pool);
    tokens.emplace_back("sessions", pool);

    // Виконання логіки...

    // Очищення арени в кінці запиту
    g_per_thread_arena.reset();
}
