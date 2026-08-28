#include <iostream>
#include <cstdint>
#include <format>

int main() {
    constexpr std::uint64_t original_id = 9007199254740993ULL; // 2^53 + 1

    // Парсинг числа у звичайний double (стандартна поведінка generic парсерів)
    const double parsed_as_double = static_cast<double>(original_id);
    const auto recovered_id = static_cast<std::uint64_t>(parsed_as_double);

    std::cout << std::format("Початковий ID:    {}\n", original_id);
    std::cout << std::format("Після double:     {}\n", recovered_id);
    std::cout << std::format("Втрата точності:  {}\n", 
                             (original_id != recovered_id) ? "ТАК (значення змінено!)" : "НІ");

    return 0;
}
