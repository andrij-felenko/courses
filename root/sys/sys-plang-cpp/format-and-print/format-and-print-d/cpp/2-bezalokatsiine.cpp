#include <format>
#include <array>
#include <string_view>
#include <iostream>

void safe_stack_log(int id, double temperature) {
    // Фіксований буфер на стеку — 0 алокацій у купі!
    std::array<char, 64> stack_buf;

    // Залишаємо 1 байт під нульовий термінатор
    auto res = std::format_to_n(stack_buf.data(), stack_buf.size() - 1, 
                                "Sensor #{}: temp = {:.2f} C", id, temperature);

    // Завершуємо рядок
    *res.out = '\0';

    std::cout << "Logged: " << stack_buf.data() << " (Total chars: " << res.size << ")\n";
}
