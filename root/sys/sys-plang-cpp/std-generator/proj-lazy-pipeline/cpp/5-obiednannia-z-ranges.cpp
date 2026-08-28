int main() {
    const std::string log_file = "system.log";

    // Побудова конвеєра:
    // 1. Отримуємо генератор парсингу логів
    // 2. Фільтруємо лише критичні помилки "ERROR" або "CRITICAL"
    // 3. Беремо перші 5 записів
    auto critical_errors = parse_logs(log_file)
        | std::views::filter([](const LogEntry& e) {
              return e.level == "ERROR" || e.level == "CRITICAL";
          })
        | std::views::take(5);

    std::cout << "--- КРИТИЧНІ ПОМИЛКИ (перші 5) ---\n";
    for (const LogEntry& err : critical_errors) {
        std::cout << "[" << err.timestamp << "] (" << err.level << "): " 
                  << err.message << "\n";
    }

    // Рекурсивне сканування диска з обмеженням кількості
    std::cout << "\n--- СКАНУВАННЯ ДЕРЕВА КАТАЛОГІВ ---\n";
    auto cpp_files = scan_tree(".")
        | std::views::filter([](const fs::directory_entry& e) {
              return e.path().extension() == ".cpp";
          })
        | std::views::take(10);

    for (const auto& entry : cpp_files) {
        std::cout << "Знайдено C++ файл: " << entry.path() << "\n";
    }

    return 0;
}
