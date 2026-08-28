#include <format>
#include <string>

void log_status(int code, const std::string& message) {
    // Коректно: компілятор розбирає "{}: {}" і звіряє кількість та типи аргументів
    std::string s = std::format("Error {}: {}", code, message);

    // ПОМИЛКА КОМПІЛЯЦІЇ: форматний рядок очікує два аргументи, а передано один!
    // std::string bad = std::format("Error {}: {}", code);
}
