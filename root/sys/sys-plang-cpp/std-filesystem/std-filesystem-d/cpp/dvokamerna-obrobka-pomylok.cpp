#include <iostream>
#include <filesystem>
#include <system_error>

namespace fs = std::filesystem;

void error_handling_comparison(const fs::path& target_path) {
    // Варіант А: Обробка через винятки (зручно у прикладному коді)
    try {
        std::uintmax_t sz = fs::file_size(target_path);
        std::cout << "Розмір: " << sz << "\n";
    } catch (const fs::filesystem_error& ex) {
        std::cerr << "Виняток: " << ex.what() << "\n"
                  << " Код:   " << ex.code().message() << "\n"
                  << " Шлях 1: " << ex.path1() << "\n";
    }

    // Варіант Б: Обробка через error_code (ідеально для системного коду без винятків)
    std::error_code ec;
    std::uintmax_t sz = fs::file_size(target_path, ec);
    if (ec) {
        std::cerr << "Помилка (без винятку): " << ec.message() 
                  << " [значення: " << ec.value() << "]\n";
    } else {
        std::cout << "Розмір: " << sz << "\n";
    }
}
