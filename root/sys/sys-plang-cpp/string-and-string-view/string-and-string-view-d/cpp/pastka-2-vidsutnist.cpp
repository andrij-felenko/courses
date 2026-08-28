void open_file(std::string_view path) {
    // ПОМИЛКА: path.data() не має '\0' на кінці, якщо це sv.substr(...)
    FILE* f = fopen(path.data(), "r"); // Небезпека!
}

// Правильно: явне створення об'єкта std::string з нульовим термінатором
void open_file_safe(std::string_view path) {
    std::string null_terminated_path(path);
    FILE* f = fopen(null_terminated_path.c_str(), "r"); // Безпечно
}
