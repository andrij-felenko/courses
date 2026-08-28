#include <iostream>
#include <array>
#include <vector>
#include <span>
#include <cstdint>
#include <string_view>

template <size_t N, int32_t Q>
class CycloPoly {
public:
    static constexpr size_t Dimension = N;
    static constexpr int32_t Modulus = Q;

    std::array<int32_t, N> coeffs{};

    constexpr CycloPoly() = default;

    constexpr CycloPoly(std::initializer_list<int32_t> list) {
        size_t idx = 0;
        for (auto val : list) {
            if (idx >= N) break;
            coeffs[idx++] = normalize(val);
        }
    }

    static constexpr int32_t normalize(int32_t val) noexcept {
        int32_t r = val % Q;
        return (r < 0) ? (r + Q) : r;
    }

    CycloPoly operator+(const CycloPoly& other) const noexcept {
        CycloPoly res;
        for (size_t i = 0; i < N; ++i) {
            res.coeffs[i] = normalize(coeffs[i] + other.coeffs[i]);
        }
        return res;
    }

    CycloPoly operator-(const CycloPoly& other) const noexcept {
        CycloPoly res;
        for (size_t i = 0; i < N; ++i) {
            res.coeffs[i] = normalize(coeffs[i] - other.coeffs[i]);
        }
        return res;
    }

    CycloPoly operator*(int32_t scalar) const noexcept {
        CycloPoly res;
        int32_t s = normalize(scalar);
        for (size_t i = 0; i < N; ++i) {
            res.coeffs[i] = normalize(coeffs[i] * s);
        }
        return res;
    }

    /* Негациклічне множення за модулем x^N + 1 та Q */
    CycloPoly operator*(const CycloPoly& other) const noexcept {
        std::array<int64_t, 2 * N> prod{};

        /* 1. Згортка коефіцієнтів */
        for (size_t i = 0; i < N; ++i) {
            for (size_t j = 0; j < N; ++j) {
                prod[i + j] += static_cast<int64_t>(coeffs[i]) * static_cast<int64_t>(other.coeffs[j]);
            }
        }

        /* 2. Негациклічна редукція: x^(N + k) = -x^k */
        CycloPoly res;
        for (size_t i = 0; i < N; ++i) {
            int64_t diff = prod[i] - prod[i + N];
            res.coeffs[i] = normalize(static_cast<int32_t>(diff % Q));
        }
        return res;
    }

    void print(std::string_view label) const {
        std::cout << label << ": [";
        for (size_t i = 0; i < N; ++i) {
            std::cout << coeffs[i] << (i + 1 < N ? ", " : "");
        }
        std::cout << "]\n";
    }
};

int main() {
    using Ring8 = CycloPoly<8, 97>;

    Ring8 a{3, 2, 0, 0, 0, 0, 0, 1}; // a(x) = 3 + 2x + x^7
    Ring8 b{5, 0, 4, 0, 0, 0, 0, 2}; // b(x) = 5 + 4x^2 + 2x^7

    auto sum = a + b;
    auto prod = a * b;

    std::cout << "=== C++ Арифметика в круговому кільці Z_97[x] / (x^8 + 1) ===\n";
    a.print("a(x)");
    b.print("b(x)");
    sum.print("a(x) + b(x)");
    prod.print("a(x) * b(x) mod (x^8 + 1)");

    return 0;
}
