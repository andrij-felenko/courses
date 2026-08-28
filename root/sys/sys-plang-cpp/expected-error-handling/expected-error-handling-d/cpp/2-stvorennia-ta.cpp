#include <expected>
#include <string>

// Функція обчислення математичного квадратного кореня
std::expected<double, std::string> safe_sqrt(double val) {
    if (val < 0.0) {
        // Явне конструювання помилки через std::unexpected
        return std::unexpected("Спроба обчислити квадратний корінь з від'ємного числа");
    }
    return std::sqrt(val); // Автоматичне неявне конструювання T у буфері
}

// In-place конструювання складної помилки без копіювання
std::expected<std::string, ComplexError> parse_data() {
    // Тег std::unexpect передає аргументи безпосередньо в конструктор ComplexError
    return std::expected<std::string, ComplexError>(std::unexpect, "Помилка парсингу", 500);
}
