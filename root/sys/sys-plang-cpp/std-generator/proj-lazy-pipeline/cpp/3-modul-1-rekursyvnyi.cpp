#include <generator>
#include <filesystem>
#include <iostream>
#include <string_view>
#include <ranges>

namespace fs = std::filesystem;

// Рекурсивний корутинний генератор файлів
std::generator<fs::directory_entry> scan_tree(fs::path dir) {
    std::error_code ec;
    auto iter = fs::directory_iterator(dir, fs::directory_options::skip_permission_denied, ec);
    
    if (ec) {
        co_return; // Помилка доступу — завершуємо корутину
    }

    for (const auto& entry : iter) {
        if (entry.is_directory(ec)) {
            // 1. Рекурсивна віддача вкладеного дерева за O(1) через elements_of
            co_yield std::ranges::elements_of(scan_tree(entry.path()));
        } else if (entry.is_regular_file(ec)) {
            // 2. Віддача окремого файла
            co_yield entry;
        }
    }
}
