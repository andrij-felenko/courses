#include <cstdint>
#include <expected>
#include <iostream>
#include <limits>
#include <utility>

// Знакове додавання: обходимо невизначену поведінку мови
// через std::expected із явною перевіркою меж діапазону.
constexpr auto checked_add(std::int8_t a, std::int8_t b) noexcept
    -> std::expected<std::int8_t, const char*> {
    if (b > 0 && a > std::numeric_limits<std::int8_t>::max() - b) {
        return std::unexpected("переповнення вгору");
    }
    if (b < 0 && a < std::numeric_limits<std::int8_t>::min() - b) {
        return std::unexpected("переповнення вниз");
    }
    return static_cast<std::int8_t>(a + b);
}

// Повертає пару (значення в слові, прапорець V) — ідіоматичний аналог overflowing_add
constexpr auto overflowing_add(std::int8_t a, std::int8_t b) noexcept
    -> std::pair<std::int8_t, bool> {
    const auto res = checked_add(a, b);
    if (!res) {
        // У слові лишається обгорнутий результат за модулем 256
        const auto wrapped = static_cast<std::int8_t>(
            static_cast<std::uint8_t>(a) + static_cast<std::uint8_t>(b));
        return {wrapped, true};
    }
    return {*res, false};
}

int main() {
    // 1. Знакове: перевіряємо переповнення ДО операції (+127 + 1 = −128)
    constexpr std::int8_t a = 127;
    constexpr std::int8_t b = 1;

    const auto [s, v] = overflowing_add(a, b);
    if (v) {
        std::cout << "знакове вискочило, у слові лишилось "
                  << static_cast<int>(s) << '\n'; // −128
    }

    // 2. Беззнакове: відновлення переносу cₙ порівнянням результату
    constexpr std::uint8_t A = 200;
    constexpr std::uint8_t B = 100;
    const auto S = static_cast<std::uint8_t>(A + B); // 300 → 44
    const bool carry = (S < A);

    std::cout << static_cast<int>(A) << " + " << static_cast<int>(B)
              << " = " << static_cast<int>(S)
              << ", перенос = " << carry << '\n'; // 44, 1

    return 0;
}
