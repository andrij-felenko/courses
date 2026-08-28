#include <iostream>
#include <cstdint>
#include <optional>
#include <concepts>
#include <type_traits>

namespace mersenne {

// Концепт C++20 для затискання беззнакових цілочисельних типів
template<typename T>
concept UnsignedInteger = std::is_unsigned_v<T>;

// Безділильне модульне зведення за модулем (2^n - 1) у стилі сучасного C++
template<UnsignedInteger T>
[[nodiscard]] constexpr T fast_modulo(T x, uint32_t n) noexcept {
    const T mask = (T{1} << n) - T{1};
    while (x > mask) {
        const T high = x >> n;
        const T low = x & mask;
        x = high + low;
    }
    return (x == mask) ? T{0} : x;
}

// Структура для повернення багатого результату факторизації
struct FactorResult {
    uint64_t factor; // Знайдений простий дільник q
    uint64_t k_step; // Крок k у прогресії q = 2*k*p + 1
};

// Оптимізований пошук дільника M_p = 2^p - 1 із поверненням std::optional
[[nodiscard]] std::optional<FactorResult> find_factor(uint32_t p, uint64_t max_k) noexcept {
    const uint64_t m_val = (p < 63) ? ((1ULL << p) - 1ULL) : 0;

    for (uint64_t k = 1; k <= max_k; ++k) {
        const uint64_t q = 2 * k * p + 1;

        // Перевірка межі квадратного кореня
        if (p < 63 && q * q > m_val) {
            break;
        }

        // Фільтр 1: Перевірка квадратичного залишку q ≡ ±1 (mod 8)
        const uint64_t mod8 = q % 8;
        if (mod8 != 1 && mod8 != 7) {
            continue;
        }

        // Фільтр 2: Модульне піднесення 2^p mod q
        uint64_t base = 2;
        uint64_t exp = p;
        uint64_t rem = 1;
        while (exp > 0) {
            if (exp & 1) {
                rem = static_cast<unsigned __int128>(rem) * base % q;
            }
            base = static_cast<unsigned __int128>(base) * base % q;
            exp >>= 1;
        }

        if (rem == 1) {
            return FactorResult{.factor = q, .k_step = k};
        }
    }

    return std::nullopt;
}

} // namespace mersenne

int main() {
    std::cout << "=== Демонстрація модульної арифметики Мерсенна (C++20) ===\n\n";

    // Тест 1: Швидке зведення за модулем M_19 = 524287
    constexpr uint64_t val = 9876543210ULL;
    constexpr uint32_t bits = 19;
    constexpr auto res_fast = mersenne::fast_modulo(val, bits);
    std::cout << "Тест 1 (val = " << val << ", n = " << bits << "):\n";
    std::cout << "  C++ Fast mod result: " << res_fast << "\n\n";

    // Тест 2: Пошук дільника M_11
    if (auto res = mersenne::find_factor(11, 50)) {
        std::cout << "Тест 2 (M_11):\n";
        std::cout << "  Дільник: " << res->factor << " (крок k = " << res->k_step << ")\n\n";
    }

    // Тест 3: Пошук дільника M_23
    if (auto res = mersenne::find_factor(23, 50)) {
        std::cout << "Тест 3 (M_23):\n";
        std::cout << "  Дільник: " << res->factor << " (крок k = " << res->k_step << ")\n\n";
    }

    // Тест 4: Пошук дільника M_29
    if (auto res = mersenne::find_factor(29, 1000)) {
        std::cout << "Тест 4 (M_29):\n";
        std::cout << "  Дільник: " << res->factor << " (крок k = " << res->k_step << ")\n\n";
    }

    return 0;
}
