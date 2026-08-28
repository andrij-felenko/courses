// main.cpp — Демонстрація високорівневого C++ API
#include <iostream>
#include "catalan_utils.hpp"

int main() {
    // 1. Обчислення значення
    if (auto c10 = catalan::CatalanCalculator::compute(10)) {
        std::cout << "C_10 = " << *c10 << "\n";
    }

    // 2. Валідація рядка Dyck
    constexpr std::string_view seq = "((()()))";
    if (catalan::CatalanCalculator::validate_dyck_path(seq)) {
        std::cout << "Послідовність " << seq << " є валідною.\n";
    }

    // 3. Генерація послідовності
    try {
        auto table = catalan::CatalanCalculator::generate_sequence(5);
        std::cout << "Перші 6 чисел Каталана: ";
        for (auto v : table) {
            std::cout << v << " ";
        }
        std::cout << "\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
    }

    return 0;
}
