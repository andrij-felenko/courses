// C++20 Idiomatic Implementation using Modern Metaprogramming & Types
#include <iostream>
#include <optional>
#include <cstdint>
#include <concepts>
#include <utility>

namespace numtheory {

// Концепт цілочисельного типу
template <typename T>
concept UnsignedInteger = std::is_unsigned_v<T> && sizeof(T) >= 4;

// Клас Модульної Арифметики із захистом від переповнення
template <UnsignedInteger T>
class ModularArithmetic {
public:
    static constexpr T mul(T a, T b, T mod) noexcept {
#if defined(__SIZEOF_INT128__)
        if constexpr (sizeof(T) <= 8) {
            return static_cast<T>((static_cast<unsigned __int128>(a) * b) % mod);
        }
#endif
        T res = 0;
        a %= mod;
        while (b > 0) {
            if (b & 1) res = (res >= mod - a) ? (res + a - mod) : (res + a);
            a = (a >= mod - a) ? (a + a - mod) : (a + a);
            b >>= 1;
        }
        return res;
    }

    static constexpr T pow(T base, T exp, T mod) noexcept {
        T res = 1;
        base %= mod;
        while (exp > 0) {
            if (exp & 1) res = mul(res, base, mod);
            base = mul(base, base, mod);
            exp >>= 1;
        }
        return res;
    }

    static constexpr int legendre(T a, T p) noexcept {
        if (a % p == 0) return 0;
        T res = pow(a, (p - 1) / 2, p);
        return (res == 1) ? 1 : -1;
    }
};

// Результат добування кореня
struct SquareRoots {
    std::uint64_t root1;
    std::uint64_t root2;
};

// Клас розв'язувача порівняння x^2 ≡ a (mod p)
class QuadraticResidueSolver {
public:
    using Arith = ModularArithmetic<std::uint64_t>;

    static std::optional<SquareRoots> solve(std::uint64_t a, std::uint64_t p) {
        a %= p;
        if (a == 0) return SquareRoots{0, 0};
        
        if (Arith::legendre(a, p) != 1) {
            return std::nullopt; // Квадратичний нелишок
        }

        // Швидка гілка для p ≡ 3 (mod 4)
        if ((p & 3) == 3) {
            std::uint64_t r = Arith::pow(a, (p + 1) / 4, p);
            return SquareRoots{r, p - r};
        }

        // Алгоритм Тонеллі-Шенкса для p ≡ 1 (mod 4)
        std::uint64_t q = p - 1;
        std::uint64_t s = 0;
        while ((q & 1) == 0) {
            q >>= 1;
            s++;
        }

        std::uint64_t z = 2;
        while (Arith::legendre(z, p) != -1) {
            z++;
        }

        std::uint64_t c = Arith::pow(z, q, p);
        std::uint64_t r = Arith::pow(a, (q + 1) / 2, p);
        std::uint64_t t = Arith::pow(a, q, p);
        std::uint64_t m = s;

        while (t != 1) {
            std::uint64_t t2i = t;
            std::uint64_t i = 0;
            for (i = 1; i < m; ++i) {
                t2i = Arith::mul(t2i, t2i, p);
                if (t2i == 1) break;
            }

            if (i == m) return std::nullopt;

            std::uint64_t b = Arith::pow(c, 1ULL << (m - i - 1), p);
            r = Arith::mul(r, b, p);
            std::uint64_t b2 = Arith::mul(b, b, p);
            t = Arith::mul(t, b2, p);
            c = b2;
            m = i;
        }

        return SquareRoots{r, p - r};
    }
};

} // namespace numtheory

int main() {
    constexpr std::uint64_t p = 1000000007ULL;
    constexpr std::uint64_t a = 5ULL;

    if (auto roots = numtheory::QuadraticResidueSolver::solve(a, p)) {
        std::cout << "Корені рівняння x^2 ≡ " << a << " (mod " << p << "):\n";
        std::cout << "x1 = " << roots->root1 << "\n";
        std::cout << "x2 = " << roots->root2 << "\n";
        
        std::uint64_t check = numtheory::ModularArithmetic<std::uint64_t>::mul(roots->root1, roots->root1, p);
        std::cout << "Перевірка: " << roots->root1 << "^2 mod " << p << " = " << check << "\n";
    } else {
        std::cout << "Розв'язку не існує!\n";
    }
    return 0;
}
