int main() {
    std::vector<UserRecord> table = {
        {1, "alice"},
        {2, "bob"},
        {3, "admin"}
    };

    // 1. Одноразова компіляція плану
    auto plan = PreparedPlan::compile("SELECT * FROM users WHERE name = ?");
    if (!plan) {
        std::cerr << "Помилка компіляції шаблону\n";
        return 1;
    }

    // 2. Передача шкідливого вхідного значення як параметра
    std::vector<Value> params = { std::string("admin' OR '1'='1") };

    auto results = VirtualMachine::execute(*plan, params, table);

    std::cout << "Знайдено рядків: " << results.size() << "\n";
    for (const auto& row : results) {
        std::cout << "  id: " << row.id << ", name: " << row.name << "\n";
    }
    // Результат: Знайдено рядків: 0
    // Байт-код не змінився; лапки та оператор OR трактуються виключно як текст.
    return 0;
}
