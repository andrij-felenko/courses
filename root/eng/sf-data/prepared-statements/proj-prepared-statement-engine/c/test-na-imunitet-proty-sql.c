int main() {
    UserRecord table[3] = {
        {1, "alice"},
        {2, "bob"},
        {3, "admin"}
    };

    // 1. Компіляція плану (виконується 1 раз при запуску)
    PreparedPlan plan;
    if (!compile_plan("SELECT * FROM users WHERE name = ?", &plan)) {
        fprintf(stderr, "Помилка компіляції шаблону\n");
        return 1;
    }

    // 2. Спроба атаки SQL-ін'єкцією через параметр зв'язування
    Value malicious_param;
    malicious_param.type = VAL_STR;
    strncpy(malicious_param.as.str, "admin' OR '1'='1", sizeof(malicious_param.as.str) - 1);

    UserRecord results[10];
    size_t count = vm_execute(&plan, &malicious_param, table, 3, results);

    printf("Знайдено рядків: %zu\n", count);
    for (size_t i = 0; i < count; i++) {
        printf("  id: %lld, name: %s\n", (long long)results[i].id, results[i].name);
    }
    // Результат: Знайдено рядків: 0
    // Рядок "admin' OR '1'='1" порівнюється як єдине строкове значення!
    return 0;
}
