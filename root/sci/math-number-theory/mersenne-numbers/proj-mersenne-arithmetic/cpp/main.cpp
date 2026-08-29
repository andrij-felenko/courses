#include <iostream>
#include <cstdint>
#include <optional>
#include <concepts>
#include <type_traits>
#include <string_view>

namespace mersenne {

// Концепт C++20 для обмеження шаблонних аргументів лише беззнаковими цілими типами
template<typename T>
concept UnsignedInteger = std::is_unsigned_v<T>;

// Шаблонний клас кільця лишків за модулем Мерсенна M_N = 2^N - 1
template<uint32_t N>
requires (N >= 1 && N <= 63)
class MersenneRing {
public:
    static constexpr uint64_t Modulus = (1ULL << N) - 1ULL;
    static constexpr uint32_t Bits = N;

    // Безділильне приведення значення x за модулем 2^N - 1
    template<UnsignedInteger T>
    [[nodiscard]] static constexpr uint64_t reduce(T x) noexcept {
        const uint64_t mask = Modulus;
        uint64_t val = static_cast<uint64_t>(x);
        while (val > mask) {
            const uint64_t high = val >> N;
            const uint64_t low = val & mask;
            val = high + low;
        }
        return (val == mask) ? 0ULL : val;
    }

    // Додавання у кільці лишків
    [[nodiscard]] static constexpr uint64_t add(uint64_t a, uint64_t b) noexcept {
        const uint64_t sum = a + b;
        return (sum >= Modulus) ? (sum - Modulus) : sum;
    }

    // Швидке множення у кільці лишків без апаратного ділення
    [[nodiscard]] static constexpr uint64_t mul(uint64_t a, uint64_t b) noexcept {
        const unsigned __int128 prod = static_cast<unsigned __int128>(a) * static_cast<unsigned __int128>(b);
        const unsigned __int128 mask = Modulus;
        unsigned __int128 val = prod;
        while (val > mask) {
            const unsigned __int128 high = val >> N;
            const unsigned __int128 low = val & mask;
            val = high + low;
        }
        const uint64_t res = static_cast<uint64_t>(val);
        return (res == Modulus) ? 0ULL : res;
    }

    // Модульне піднесення до степеня за алгоритмом бінарного піднесення
    [[nodiscard]] static constexpr uint64_t pow(uint64_t base, uint64_t exp) noexcept {
        uint64_t result = 1ULL;
        base = reduce(base);
        while (exp > 0ULL) {
            if (exp & 1ULL) {
                result = mul(result, base);
            }
            base = mul(base, base);
            exp >>= 1ULL;
        }
        return result;
    }
};

// Структура результату факторизації числа Мерсенна
struct FactorResult {
    uint64_t factor; // Знайдений простий дільник q
    uint64_t k_step; // Номер кроку k в арифметичній прогресії q = 2*k*p + 1
};

// Загальне модульне піднесення до степеня 2^p mod q
[[nodiscard]] constexpr uint64_t mod_pow2(uint32_t p, uint64_t q) noexcept {
    uint64_t base = 2ULL % q;
    uint64_t exp = p;
    uint64_t rem = 1ULL;
    while (exp > 0ULL) {
        if (exp & 1ULL) {
            rem = static_cast<uint64_t>((static_cast<unsigned __int128>(rem) * base) % q);
        }
        base = static_cast<uint64_t>((static_cast<unsigned __int128>(base) * base) % q);
        exp >>= 1ULL;
    }
    return rem;
}

// Оптимізований пошук дільника M_p = 2^p - 1 з подвійною теоретико-числовою фільтрацією
[[nodiscard]] std::optional<FactorResult> find_factor(uint32_t p, uint64_t max_k) noexcept {
    const uint64_t m_val = (p < 63) ? ((1ULL << p) - 1ULL) : 0ULL;

    for (uint64_t k = 1ULL; k <= max_k; ++k) {
        const uint64_t q = 2ULL * k * static_cast<uint64_t>(p) + 1ULL;

        // Перевірка межі квадратного кореня для 64-бітних значень
        if (p < 63 && m_val > 0ULL && q > m_val / q) {
            break;
        }

        // Фільтр 1: Перевірка квадратичного залишку q ≡ ±1 (mod 8)
        const uint64_t mod8 = q & 7ULL;
        if (mod8 != 1ULL && mod8 != 7ULL) {
            continue;
        }

        // Фільтр 2: Перевірка конгруенції 2^p ≡ 1 (mod q)
        if (mod_pow2(p, q) == 1ULL) {
            return FactorResult{.factor = q, .k_step = k};
        }
    }

    return std::nullopt;
}

// Перевірка правильності знайденого дільника
[[nodiscard]] constexpr bool verify_factor(uint32_t p, uint64_t factor) noexcept {
    if (factor == 0ULL) return false;
    return mod_pow2(p, factor) == 1ULL;
}

} // namespace mersenne

int main() {
    std::cout << "=== Демонстрація модульної арифметики Мерсенна (C++20) ===\n\n";

    // Тест 1: Робота з кільцем лишків за модулем M_19 = 2^19 - 1 = 524287
    using Ring19 = mersenne::MersenneRing<19>;
    constexpr uint64_t test_val = 9876543210ULL;
    constexpr uint64_t reduced = Ring19::reduce(test_val);
    constexpr uint64_t slow_mod = test_val % Ring19::Modulus;
    
    std::cout << "Тест 1: Кільце лишків MersenneRing<19> (модуль " << Ring19::Modulus << "):\n";
    std::cout << "  Вхідне число:     " << test_val << "\n";
    std::cout << "  Швидке зведення:  " << reduced << "\n";
    std::cout << "  Еталонний залишок: " << slow_mod << "\n";
    std::cout << "  Співпадіння:      " << ((reduced == slow_mod) ? "ТАК" : "НІ") << "\n\n";

    // Тест 2: Множення та піднесення до степеня у кільці MersenneRing<13> (M_13 = 8191)
    using Ring13 = mersenne::MersenneRing<13>;
    constexpr uint64_t mul_res = Ring13::mul(1234, 5678);
    constexpr uint64_t pow_res = Ring13::pow(2, 26); // (2^13)^2 = 1^2 = 1 mod 8191
    std::cout << "Тест 2: Алгебраїчні операції у MersenneRing<13>:\n";
    std::cout << "  (1234 * 5678) mod 8191 = " << mul_res << "\n";
    std::cout << "  (2^26) mod 8191        = " << pow_res << " (очікується 1)\n\n";

    // Тест 3: Факторизація складених чисел Мерсенна за допомогою find_factor
    auto run_factor_test = [](uint32_t p, uint64_t max_k, std::string_view name) {
        std::cout << "Тест факторизації для " << name << " (p = " << p << "):\n";
        if (const auto res = mersenne::find_factor(p, max_k)) {
            std::cout << "  Знайдено дільник: " << res->factor 
                      << " на кроці k = " << res->k_step << "\n";
            std::cout << "  Верифікація:      " 
                      << (mersenne::verify_factor(p, res->factor) ? "УСПІШНО" : "ПОМИЛКА") << "\n";
        } else {
            std::cout << "  Дільник не знайдено в межах k <= " << max_k << "\n";
        }
        std::cout << "\n";
    };

    run_factor_test(11, 100, "M_11 = 2047");
    run_factor_test(23, 100, "M_23 = 8388607");
    run_factor_test(29, 1000, "M_29 = 536870911");

    return 0;
}
