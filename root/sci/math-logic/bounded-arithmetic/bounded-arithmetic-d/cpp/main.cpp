// Ідіоматична реалізація операторів обмеженої арифметики мовою C++
#include <iostream>
#include <cstdint>
#include <optional>
#include <vector>
#include <bit>
#include <span>

namespace bounded_arithmetic {

// Обчислення бітової довжини |x| через бітові операції
[[nodiscard]] constexpr std::uint32_t bit_length(std::uint64_t x) noexcept {
    if (x == 0) return 0;
    return static_cast<std::uint32_t>(std::bit_width(x));
}

// Обчислення функції smash: x # y = 2^{|x| * |y|}
[[nodiscard]] constexpr std::optional<std::uint64_t> smash(std::uint64_t x, std::uint64_t y) noexcept {
    const std::uint32_t len_x = bit_length(x);
    const std::uint32_t len_y = bit_length(y);
    const std::uint64_t exponent = static_cast<std::uint64_t>(len_x) * len_y;

    if (exponent >= 64) {
        return std::nullopt; // Безпечна обробка арифметичного переповнення
    }

    return std::uint64_t{1} << exponent;
}

// Префіксний ітератор PIND: виконує індуктивний синтез за |x| кроків
template <typename State, typename StepCombinator>
[[nodiscard]] State execute_pind(std::uint64_t x, State initial_state, StepCombinator step) {
    if (x == 0) return initial_state;

    std::vector<std::uint64_t> prefix_stack;
    prefix_stack.reserve(64);

    for (std::uint64_t curr = x; curr > 0; curr >>= 1) {
        prefix_stack.push_back(curr);
    }

    State current_state = initial_state;
    // Розгортання префіксного шляху довжини |x|
    for (auto it = prefix_stack.rbegin(); it != prefix_stack.rend(); ++it) {
        current_state = step(current_state, *it);
    }

    return current_state;
}

} // namespace bounded_arithmetic
