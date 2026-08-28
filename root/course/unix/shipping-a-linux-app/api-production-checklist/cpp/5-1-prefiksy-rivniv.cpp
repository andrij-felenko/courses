#include <iostream>
#include <string_view>
#include <format>

// Друк логів для journald мовою C++23
void log_service_events(std::string_view db_name, int port) {
    std::cout << std::format("<6>Ініціалізація мережевого сервера на порту {} успішна\n", port);
    std::cerr << std::format("<3>Помилка відкриття файлу бази даних '{}': файл не знайдено\n", db_name);
    std::cout.flush();
    std::cerr.flush();
}
