// src/main.cpp — сучасна реалізація утиліти на мові C++20
#include <iostream>
#include <span>
#include <vector>
#include "diag/config.h"
#include "diag/version.hpp"

int main() {
    std::cout << "========================================\n";
    std::cout << diag::version::project_name << " (C++20 клієнт)\n";
    std::cout << "========================================\n";
    std::cout << "Версія продукту: " << diag::version::version_string
              << " (компоненти: " << diag::version::major << "."
              << diag::version::minor << "." << diag::version::patch << ")\n";
    std::cout << "Git ревізія:     " << diag::version::git_commit_hash
              << " [гілка: " << diag::version::git_branch << "]";

    if constexpr (diag::version::is_dirty_tree) {
        std::cout << " [УВАГА: незакомічені локальні зміни!]";
    }
    std::cout << "\n----------------------------------------\n";

    // Безпечне розгалуження часу компіляції за допомогою if constexpr
    if constexpr (DIAG_ENABLE_ZSTD) {
        std::cout << "Стиснення даних: Zstandard скомпільовано в бінарний файл\n";
    } else {
        std::cout << "Стиснення даних: пряма передача без пакування\n";
    }

    if constexpr (DIAG_ENABLE_TRACING) {
        std::cout << "Діагностика: активовано високоточні лічильники подій\n";
    }

    std::cout << "Розмір внутрішнього буфера: " << DIAG_BUFFER_SIZE << " байтів\n";
    return 0;
}
