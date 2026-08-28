#include <iostream>
#include <vector>
#include <algorithm>
#include <cstdint>
#include <optional>
#include <iomanip>

struct PowerItem {
    std::uint64_t val;
    std::uint32_t base;
    std::uint32_t exp;
};

class CatalanVerifier {
public:
    // Швидке модульне піднесення до степеня з 128-бітною проміжною арифметикою
    static std::uint64_t mod_pow(std::uint64_t base, std::uint64_t exp, std::uint64_t mod) noexcept {
        std::uint64_t result = 1;
        base %= mod;
        while (exp > 0) {
            if (exp & 1) {
                result = static_cast<unsigned __int128>(result) * base % mod;
            }
            base = static_cast<unsigned __int128>(base) * base % mod;
            exp >>= 1;
        }
        return result;
    }

    // Перевірка подвійної умови Віферіха для двох простих чисел
    static bool is_wieferich_pair(std::uint64_t p, std::uint64_t q) noexcept {
        if (p <= 1 || q <= 1 || p == q) return false;
        const std::uint64_t q2 = q * q;
        const std::uint64_t p2 = p * p;
        return (mod_pow(p, q - 1, q2) == 1) && (mod_pow(q, p - 1, p2) == 1);
    }

    // Генерація та унікалізація точних степенів у векторі C++ STL
    static std::vector<PowerItem> scan_powers(std::uint64_t limit) {
        std::vector<PowerItem> powers;
        powers.reserve(2048);

        for (std::uint64_t u = 2; u * u <= limit; ++u) {
            std::uint64_t val = u * u;
            std::uint32_t v = 2;
            while (val <= limit) {
                powers.push_back({val, static_cast<std::uint32_t>(u), v});
                if (limit / u < val) break; // Забігання переповнення 64 біт
                val *= u;
                ++v;
            }
        }

        std::sort(powers.begin(), powers.end(), [](const PowerItem& a, const PowerItem& b) noexcept {
            return a.val < b.val;
        });

        // Видалення дублікатів однакових значень (наприклад, 4^2 та 2^4)
        powers.erase(std::unique(powers.begin(), powers.end(), [](const PowerItem& a, const PowerItem& b) noexcept {
            return a.val == b.val;
        }), powers.end());

        return powers;
    }
};

int main() {
    constexpr std::uint64_t limit = 100000;
    std::cout << "Пошук сусідніх степенів (C++) до N = " << limit << "...\n";
    
    const auto powers = CatalanVerifier::scan_powers(limit);
    for (std::size_t i = 0; i + 1 < powers.size(); ++i) {
        if (powers[i + 1].val - powers[i].val == 1) {
            std::cout << "Знайдено розв'язок: "
                      << powers[i + 1].base << "^" << powers[i + 1].exp << " - "
                      << powers[i].base << "^" << powers[i].exp << " = "
                      << powers[i + 1].val << " - " << powers[i].val << " = 1\n";
        }
    }

    return 0;
}
