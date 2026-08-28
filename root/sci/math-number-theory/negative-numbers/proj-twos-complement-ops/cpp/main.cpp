#include <iostream>
#include <cstdint>
#include <cmath>
#include <limits>
#include <utility>
#include <optional>
#include <stdexcept>
#include <iomanip>

namespace math {

// Структура результату Евклідового ділення
struct EuclideanResult {
    std::int64_t quot; // Частка q
    std::int64_t rem;  // Остача r, 0 <= r < |b|
};

// Евклідове ділення: a = q*b + r, 0 <= r < |b|
constexpr EuclideanResult euclidean_div(std::int64_t a, std::int64_t b) {
    if (b == 0) {
        throw std::invalid_argument("Ділення на нуль у euclidean_div");
    }

    std::int64_t q = a / b;
    std::int64_t r = a % b;

    if (r < 0) {
        if (b > 0) {
            q -= 1;
            r += b;
        } else {
            q += 1;
            r -= b;
        }
    }
    return {q, r};
}

// Безпечне знакове додавання з використанням std::optional
constexpr std::optional<std::int64_t> safe_add(std::int64_t a, std::int64_t b) noexcept {
    if ((b > 0 && a > std::numeric_limits<std::int64_t>::max() - b) ||
        (b < 0 && a < std::numeric_limits<std::int64_t>::min() - b)) {
        return std::nullopt; // Переповнення
    }
    return a + b;
}

// Безпечне знакове множення з використанням std::optional
constexpr std::optional<std::int64_t> safe_mul(std::int64_t a, std::int64_t b) noexcept {
    if (a == 0 || b == 0) return 0;
    if (a > 0) {
        if (b > 0 && a > std::numeric_limits<std::int64_t>::max() / b) return std::nullopt;
        if (b < 0 && b < std::numeric_limits<std::int64_t>::min() / a) return std::nullopt;
    } else {
        if (b > 0 && a < std::numeric_limits<std::int64_t>::min() / b) return std::nullopt;
        if (b < 0 && a < std::numeric_limits<std::int64_t>::max() / b) return std::nullopt;
    }
    return a * b;
}

// Перевірка знакового біта та обчислення додаткового коду
constexpr bool is_negative(std::int64_t val) noexcept {
    return val < 0;
}

constexpr std::uint64_t twos_complement_negate(std::int64_t val) noexcept {
    return static_cast<std::uint64_t>(~static_cast<std::uint64_t>(val)) + 1U;
}

} // namespace math

int main() {
    constexpr std::int64_t a = -13;
    constexpr std::int64_t b = 5;

    // Вбудовані оператори C++
    std::cout << "Стандартний C++ operator%: -13 % 5 = " << (a % b) << "\n";

    // Евклідове ділення
    const auto [q, r] = math::euclidean_div(a, b);
    std::cout << "Евклідове ділення: -13 = (" << q << ") * 5 + " << r << "\n";

    // Детекція переповнення
    constexpr std::int64_t max_val = std::numeric_limits<std::int64_t>::max();
    if (auto res = math::safe_add(max_val, 100)) {
        std::cout << "Сума: " << *res << "\n";
    } else {
        std::cout << "Виявлено знакове переповнення (Overflow) при додаванні!\n";
    }

    if (auto res = math::safe_mul(-1000000000LL, 10000000000LL)) {
        std::cout << "Добуток: " << *res << "\n";
    } else {
        std::cout << "Виявлено знакове переповнення (Overflow) при множенні!\n";
    }

    // Додатковий код
    constexpr std::int64_t neg_val = -42;
    std::cout << "Число -42 у додатковому коді: 0x"
              << std::hex << std::setw(16) << std::setfill('0')
              << static_cast<std::uint64_t>(neg_val) << std::dec << "\n";

    return 0;
}
