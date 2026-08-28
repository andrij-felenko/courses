#include <iostream>
#include <vector>
#include <span>
#include <array>
#include <expected>
#include <random>
#include <format>
#include <concepts>
#include <stdexcept>

namespace math {

/* --- 1. Шаблонний алгоритм Бйорка — Перейри над довільним полем --- */

enum class SolverError {
    InvalidDimensions,
    DuplicateNodes,
    SingularMatrix
};

/* Концепт для арифметичного поля */
template <typename T>
concept FieldElement = requires(T a, T b) {
    { a + b } -> std::convertible_to<T>;
    { a - b } -> std::convertible_to<T>;
    { a * b } -> std::convertible_to<T>;
    { a / b } -> std::convertible_to<T>;
    { a == b } -> std::convertible_to<bool>;
};

/*
 * Розв'язання прямої системи Вандермонда V_n * c = y.
 * Працює за час O(n^2), пам'ять O(n) з контролем помилок.
 */
template <FieldElement T>
[[nodiscard]] std::expected<std::vector<T>, SolverError>
bjorck_pereyra_solve(std::span<const T> x, std::span<const T> y) {
    const size_t n = x.size();
    if (n == 0 || y.size() != n) {
        return std::unexpected(SolverError::InvalidDimensions);
    }

    /* Перевірка лінійної незалежності вузлів */
    for (size_t i = 0; i < n; ++i) {
        for (size_t j = i + 1; j < n; ++j) {
            if (x[i] == x[j]) {
                return std::unexpected(SolverError::DuplicateNodes);
            }
        }
    }

    std::vector<T> c(y.begin(), y.end());

    /* Етап 1: Обчислення коефіцієнтів Ньютона (розділені різниці) */
    for (size_t k = 0; k < n - 1; ++k) {
        for (size_t i = n - 1; i > k; --i) {
            T denom = x[i] - x[i - k - 1];
            c[i] = (c[i] - c[i - 1]) / denom;
        }
    }

    /* Етап 2: Зворотний хід до мономіального базису */
    for (size_t k = n - 1; k > 0; --k) {
        size_t node_idx = k - 1;
        for (size_t i = node_idx; i < n - 1; ++i) {
            c[i] = c[i] - c[i + 1] * x[node_idx];
        }
    }

    return c;
}

/* --- 2. Поле Галуа GF(256) у сучасному стилі C++ --- */

class GF256 {
private:
    uint8_t val_{0};

    struct Tables {
        std::array<uint8_t, 512> exp{};
        std::array<uint8_t, 256> log{};

        constexpr Tables() {
            uint32_t current = 1;
            for (int i = 0; i < 255; ++i) {
                exp[i] = static_cast<uint8_t>(current);
                exp[i + 255] = static_cast<uint8_t>(current);
                log[current] = static_cast<uint8_t>(i);
                current <<= 1;
                if (current & 0x100) {
                    current ^= 0x11B; /* Незвідний поліном AES */
                }
            }
            log[0] = 0;
        }
    };

    static const Tables& tables() {
        static const Tables t;
        return t;
    }

public:
    constexpr GF256() = default;
    constexpr explicit GF256(uint8_t v) : val_(v) {}

    [[nodiscard]] constexpr uint8_t raw() const noexcept { return val_; }

    friend constexpr bool operator==(GF256 a, GF256 b) noexcept { return a.val_ == b.val_; }
    friend constexpr GF256 operator+(GF256 a, GF256 b) noexcept { return GF256(a.val_ ^ b.val_); }
    friend constexpr GF256 operator-(GF256 a, GF256 b) noexcept { return GF256(a.val_ ^ b.val_); }

    friend GF256 operator*(GF256 a, GF256 b) noexcept {
        if (a.val_ == 0 || b.val_ == 0) return GF256(0);
        const auto& tbl = tables();
        return GF256(tbl.exp[tbl.log[a.val_] + tbl.log[b.val_]]);
    }

    friend GF256 operator/(GF256 a, GF256 b) {
        if (b.val_ == 0) throw std::domain_error("GF(256) division by zero");
        if (a.val_ == 0) return GF256(0);
        const auto& tbl = tables();
        return GF256(tbl.exp[(tbl.log[a.val_] + 255 - tbl.log[b.val_]) % 255]);
    }
};

/* --- 3. Схема розділення секрету Шаміра --- */

struct Share {
    GF256 x;
    GF256 y;
};

class ShamirScheme {
public:
    static std::vector<Share> split(GF256 secret, size_t n, size_t k) {
        if (k > n || k == 0 || n >= 256) {
            throw std::invalid_argument("Invalid threshold or party count");
        }

        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<uint32_t> dist(1, 255);

        std::vector<GF256> coeffs(k);
        coeffs[0] = secret;
        for (size_t i = 1; i < k; ++i) {
            coeffs[i] = GF256(static_cast<uint8_t>(dist(gen)));
        }

        std::vector<Share> shares;
        shares.reserve(n);

        for (size_t i = 1; i <= n; ++i) {
            GF256 x(static_cast<uint8_t>(i));
            GF256 y = coeffs[k - 1];
            for (int j = static_cast<int>(k) - 2; j >= 0; --j) {
                y = y * x + coeffs[j];
            }
            shares.push_back({x, y});
        }
        return shares;
    }

    static GF256 recover(std::span<const Share> shares) {
        const size_t k = shares.size();
        if (k == 0) throw std::invalid_argument("Empty shares");

        GF256 secret(0);
        for (size_t i = 0; i < k; ++i) {
            GF256 num(1);
            GF256 den(1);
            for (size_t j = 0; j < k; ++j) {
                if (i == j) continue;
                num = num * shares[j].x;
                den = den * (shares[j].x + shares[i].x);
            }
            GF256 weight = num / den;
            secret = secret + shares[i].y * weight;
        }
        return secret;
    }
};

} // namespace math

int main() {
    std::cout << "=== 1. Тест Бйорка — Перейри на double (C++23) ===\n";
    std::vector<double> x_nodes = {1.0, 2.0, 4.0, 5.0};
    std::vector<double> y_vals  = {2.0, 5.0, 17.0, 26.0};

    auto result = math::bjorck_pereyra_solve<double>(x_nodes, y_vals);
    if (result.has_value()) {
        const auto& c = result.value();
        for (size_t i = 0; i < c.size(); ++i) {
            std::cout << std::format("  c[{}] = {:6.2f}\n", i, c[i]);
        }
    }

    std::cout << "\n=== 2. Тест розділення секрету Шаміра (GF(256)) ===\n";
    math::GF256 secret(0x5A);
    const size_t n = 5;
    const size_t k = 3;

    auto shares = math::ShamirScheme::split(secret, n, k);
    std::cout << std::format("Згенеровано {} часток для секрету 0x{:02X}:\n", n, secret.raw());
    for (size_t i = 0; i < shares.size(); ++i) {
        std::cout << std::format("  Учасник {}: x = {}, y = 0x{:02X}\n",
                                 i + 1, shares[i].x.raw(), shares[i].y.raw());
    }

    std::vector<math::Share> subset = {shares[1], shares[3], shares[4]};
    math::GF256 recovered = math::ShamirScheme::recover(subset);
    std::cout << std::format("Відновлений секрет за частками 2, 4, 5: 0x{:02X} ({})\n",
                             recovered.raw(), (recovered == secret ? "УСПІХ" : "ПОМИЛКА"));

    return 0;
}
