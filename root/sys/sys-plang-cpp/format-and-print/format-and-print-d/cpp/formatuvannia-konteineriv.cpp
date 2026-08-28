#include <format>
#include <vector>
#include <map>
#include <string>
#include <iostream>

int main() {
    std::vector<int> numbers = {10, 20, 30, 40};
    
    // Стандартний вивід вектора
    std::cout << std::format("{}", numbers) << "\n"; // "[10, 20, 30, 40]"

    // Внутрішній специфікатор форматування елементів (Hex з префіксом)
    std::cout << std::format("{::#x}", numbers) << "\n"; // "[0xa, 0x14, 0x1e, 0x28]"

    // Специфікатор 'n' відключає зовнішні квадратні дужки (no brackets)
    std::cout << std::format("{:n}", numbers) << "\n"; // "10, 20, 30, 40"

    // Форматування словника map
    std::map<std::string, int> items = {{"apple", 5}, {"banana", 12}};
    std::cout << std::format("{}", items) << "\n"; // "{\"apple\": 5, \"banana\": 12}"
}
