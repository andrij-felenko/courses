#include <filesystem>
#include <iostream>

namespace fs = std::filesystem;

void directory_operations_demo() {
    std::error_code ec;
    fs::path nested_dir = "sandbox/data/logs/2026";

    // Створення всього ланцюжка каталогів
    if (fs::create_directories(nested_dir, ec)) {
        std::cout << "Каталоги успішно створено!\n";
    }

    // Рекурсивне видалення з підрахунком вилучених об'єктів
    std::uintmax_t removed_count = fs::remove_all("sandbox", ec);
    std::cout << "Вилучено об'єктів: " << removed_count << "\n";
}
