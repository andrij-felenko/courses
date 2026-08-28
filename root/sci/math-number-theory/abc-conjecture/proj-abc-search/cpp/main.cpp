#include <iostream>
#include <vector>
#include <cmath>
#include <numeric>
#include <algorithm>
#include <iomanip>
#include <cstdint>
#include <span >

// Структура для збереження трійки ABC в C++
struct ABCTriple {
    std::uint64_t a{0};
    std::uint64_t b{0};
    std::uint64_t c{0};
    std::uint64_t rad_abc{0};
    double quality{0.0};
};

// Клас генерації радикалів за допомогою сита Ератосфена (RAII управління пам'яттю)
class RadicalSieve {
public:
    explicit RadicalSieve(std::size_t max_val) : rad_(max_val + 1, 1) {
        for (std::size_t p = 2; p <= max_val; ++p) {
            if (rad_[p] == 1) { // p — просте число
                for (std::size_t k = p; k <= max_val; k += p) {
                    rad_[k] *= p;
                }
            }
        }
    }

    [[nodiscard]] std::uint64_t operator[](std::size_t n) const noexcept {
        return rad_[n];
    }

    [[nodiscard]] std::size_t size() const noexcept {
        return rad_.size();
    }

private:
    std::vector<std::uint64_t> rad_;
};

// Клас для пошуку та сортування трійок ABC
class ABCFinder {
public:
    static std::vector<ABCTriple> search(std::uint64_t c_max) {
        RadicalSieve sieve(c_max);
        std::vector<ABCTriple> results;

        for (std::uint64_t c = 3; c <= c_max; ++c) {
            double log_c = std::log(static_cast<double>(c));
            double log_rad_c = std::log(static_cast<double>(sieve[c]));

            for (std::uint64_t a = 1; a <= c / 2; ++a) {
                std::uint64_t b = c - a;

                if (std::gcd(a, b) != 1) continue;

                double log_rad_a = std::log(static_cast<double>(sieve[a]));
                double log_rad_b = std::log(static_cast<double>(sieve[b]));
                double log_rad_abc = log_rad_a + log_rad_b + log_rad_c;

                if (log_c > log_rad_abc) {
                    double q = log_c / log_rad_abc;
                    std::uint64_t rad_abc = sieve[a] * sieve[b] * sieve[c];
                    results.push_back({a, b, c, rad_abc, q});
                }
            }
        }

        std::sort(results.begin(), results.end(), [](const ABCTriple& t1, const ABCTriple& t2) {
            return t1.quality > t2.quality;
        });

        return results;
    }
};

int main() {
    constexpr std::uint64_t c_max = 10000;
    auto triples = ABCFinder::search(c_max);

    std::cout << "Знайдено " << triples.size() << " трійок ABC для c <= " << c_max << ":\n";
    std::cout << std::left << std::setw(8) << "a"
              << std::setw(8) << "b"
              << std::setw(8) << "c"
              << std::setw(12) << "rad(abc)"
              << std::setw(10) << "Якість (q)" << "\n";
    std::cout << std::string(48, '-') << "\n";

    std::size_t limit = std::min<std::size_t>(triples.size(), 10);
    for (std::size_t i = 0; i < limit; ++i) {
        const auto& t = triples[i];
        std::cout << std::left << std::setw(8) << t.a
                  << std::setw(8) << t.b
                  << std::setw(8) << t.c
                  << std::setw(12) << t.rad_abc
                  << std::fixed << std::setprecision(4) << t.quality << "\n";
    }

    return 0;
}
