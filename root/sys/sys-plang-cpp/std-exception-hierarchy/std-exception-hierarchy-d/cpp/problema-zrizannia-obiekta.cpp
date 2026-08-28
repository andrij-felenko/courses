#include <iostream>
#include <stdexcept>
#include <string>

// Функція обробки файлового контейнера
void parse_config_file(const std::string& path) {
    if (path.empty()) {
        throw std::invalid_argument("Конфігураційний шлях не може бути порожнім");
    }
}

void execute_safe_operation() {
    try {
        parse_config_file("");
    } catch (const std::exception& e) { // ✓ Безпечне поліморфне посилання
        std::cout << "Успішно перехоплено: " << e.what() << std::endl;
    }
}
