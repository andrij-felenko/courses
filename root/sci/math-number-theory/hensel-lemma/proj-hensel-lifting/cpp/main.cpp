#include <iostream>
#include <vector>
#include <span>
#include <optional>
#include <cstdint>
#include <string_view>
#include <iomanip>

namespace math {

/**
 * @brief Статус результату операції підйому Гензеля.
 */
enum class HenselError {
    SingularRoot,       ///< Похідна f'(r) ≡ 0 (mod p), звичайний підйом неможливий
    NoModularInverse,   ///< Елемент не є взаємно простим із модулем
    InvalidParameters   ///< Некоректні параметри (наприклад, цільовий степінь k < 1)
};

/**
 * @brief Структура для повернення результату успішного підйому.
 */
struct LiftResult {
    std::int64_t root{0};        ///< Обчислений піднятий корінь
    std::int64_t modulus{0};     ///< Модуль p^k, за яким діє корінь
    std::size_t iterations{0};   ///< Кількість виконаних кроків
};

/**
 * @brief Обчислювач підйому Гензеля для поліноміальних порівнянь.
 */
class HenselSolver {
public:
    /**
     * @brief Безпечне приведення числа до канонічного невід'ємного залишку Z/mZ.
     */
    static constexpr std::int64_t mod_pos(std::int64_t val, std::int64_t m) noexcept {
        const std::int64_t rem = val % m;
        return (rem < 0) ? rem + m : rem;
    }

    /**
     * @brief Обчислення мультиплікативного оберненого елемента: a * x ≡ 1 (mod m).
     * @return std::optional з оберненим значенням або std::nullopt, якщо gcd(a, m) != 1.
     */
    static std::optional<std::int64_t> mod_inverse(std::int64_t a, std::int64_t m) noexcept {
        if (m <= 1) return std::nullopt;
        std::int64_t m0 = m;
        std::int64_t y = 0, x = 1;
        std::int64_t curr_a = mod_pos(a, m);

        while (curr_a > 1) {
            if (m == 0) return std::nullopt;
            std::int64_t q = curr_a / m;
            std::int64_t t = m;
            m = curr_a % m;
            curr_a = t;
            t = y;
            y = x - q * y;
            x = t;
        }
        if (curr_a != 1) return std::nullopt;
        return mod_pos(x, m0);
    }

    /**
     * @brief Обчислення значення многочлена f(x) = poly[0] + poly[1]*x + ... за схемою Горнера.
     */
    static std::int64_t eval_poly(
        std::span<const std::int64_t> poly,
        std::int64_t x,
        std::int64_t mod
    ) noexcept {
        std::int64_t res = 0;
        for (auto it = poly.rbegin(); it != poly.rend(); ++it) {
            res = mod_pos(res * x + *it, mod);
        }
        return res;
    }

    /**
     * @brief Обчислення значення формальної похідної f'(x) за модулем mod.
     */
    static std::int64_t eval_derivative(
        std::span<const std::int64_t> poly,
        std::int64_t x,
        std::int64_t mod
    ) noexcept {
        if (poly.size() <= 1) return 0;
        std::int64_t res = 0;
        for (std::size_t i = poly.size() - 1; i >= 1; --i) {
            const auto coeff = mod_pos(poly[i] * static_cast<std::int64_t>(i), mod);
            res = mod_pos(res * x + coeff, mod);
        }
        return res;
    }

    /**
     * @brief Швидке цілочисельне піднесення основи до степеня exp.
     */
    static constexpr std::int64_t int_power(std::int64_t base, std::size_t exp) noexcept {
        std::int64_t res = 1;
        for (std::size_t i = 0; i < exp; ++i) {
            res *= base;
        }
        return res;
    }

    /**
     * @brief Лінійний підйом Гензеля (крок по одному степеню p: p^1 -> p^2 -> ... -> p^k).
     */
    static std::optional<LiftResult> lift_linear(
        std::span<const std::int64_t> poly,
        std::int64_t p,
        std::size_t target_k,
        std::int64_t initial_root
    ) noexcept {
        if (poly.empty() || target_k < 1 || p < 2) return std::nullopt;

        std::int64_t current_root = mod_pos(initial_root, p);
        const std::int64_t f_prime_mod_p = eval_derivative(poly, current_root, p);

        if (f_prime_mod_p == 0) {
            return std::nullopt; // Вироджений (кратний) корінь
        }

        const auto v_inv_opt = mod_inverse(f_prime_mod_p, p);
        if (!v_inv_opt.has_value()) {
            return std::nullopt;
        }
        const std::int64_t v_inv = v_inv_opt.value();

        std::int64_t p_pow = p;
        for (std::size_t step = 1; step < target_k; ++step) {
            const std::int64_t p_next = p_pow * p;
            const std::int64_t f_val = eval_poly(poly, current_root, p_next);
            const std::int64_t q = f_val / p_pow;

            const std::int64_t t = mod_pos(-q * v_inv, p);
            current_root = mod_pos(current_root + t * p_pow, p_next);
            p_pow = p_next;
        }

        return LiftResult{current_root, p_pow, target_k - 1};
    }

    /**
     * @brief Квадратичний підйом Гензеля (подвоєння степеня модуля p^k -> p^(2k) за метод Ньютона).
     */
    static std::optional<LiftResult> lift_quadratic(
        std::span<const std::int64_t> poly,
        std::int64_t p,
        std::size_t target_k,
        std::int64_t initial_root
    ) noexcept {
        if (poly.empty() || target_k < 1 || p < 2) return std::nullopt;

        std::int64_t root = mod_pos(initial_root, p);
        const std::int64_t f_prime_p = eval_derivative(poly, root, p);
        if (f_prime_p == 0) {
            return std::nullopt; // Особливий корінь
        }

        const std::int64_t target_mod = int_power(p, target_k);
        std::int64_t current_mod = p;
        std::size_t iterations = 0;

        while (current_mod < target_mod) {
            const std::int64_t next_mod = current_mod * current_mod;
            const std::int64_t f_val = eval_poly(poly, root, next_mod);
            const std::int64_t df_val = eval_derivative(poly, root, next_mod);

            const auto inv_df_opt = mod_inverse(df_val, next_mod);
            if (!inv_df_opt.has_value()) {
                return std::nullopt;
            }

            const std::int64_t delta = mod_pos(f_val * inv_df_opt.value(), next_mod);
            root = mod_pos(root - delta, next_mod);
            current_mod = next_mod;
            ++iterations;
        }

        return LiftResult{mod_pos(root, target_mod), target_mod, iterations};
    }
};

} // namespace math

int main() {
    std::cout << "=== Демонстрація підйому Гензеля на C++ ===\n\n";

    // Тест 1: f(x) = x^2 - 7 ≡ 0 (mod 3^5 = 243)
    const std::vector<std::int64_t> poly1 = {-7, 0, 1}; // x^2 - 7
    constexpr std::int64_t p1 = 3;
    constexpr std::size_t k1 = 5;
    constexpr std::int64_t r1_init = 1;

    std::cout << "--- Тест 1: x^2 - 7 ≡ 0 (mod 3^5) ---\n";
    const auto res_linear = math::HenselSolver::lift_linear(poly1, p1, k1, r1_init);
    if (res_linear.has_value()) {
        const auto& res = res_linear.value();
        std::cout << "Лінійний підйом: корінь a_" << k1 << " = " << res.root
                  << " (mod " << res.modulus << ") за " << res.iterations << " кроків\n";
        const auto check = math::HenselSolver::eval_poly(poly1, res.root, res.modulus);
        std::cout << "Перевірка: f(" << res.root << ") mod " << res.modulus << " = " << check
                  << " (успіх: " << (check == 0 ? "ТАК" : "НІ") << ")\n";
    }

    // Тест 2: f(x) = x^3 - 2 ≡ 0 (mod 5^4 = 625)
    const std::vector<std::int64_t> poly2 = {-2, 0, 0, 1}; // x^3 - 2
    constexpr std::int64_t p2 = 5;
    constexpr std::size_t k2 = 4;
    constexpr std::int64_t r2_init = 3;

    std::cout << "\n--- Тест 2: x^3 - 2 ≡ 0 (mod 5^4) ---\n";
    const auto res_quad = math::HenselSolver::lift_quadratic(poly2, p2, k2, r2_init);
    if (res_quad.has_value()) {
        const auto& res = res_quad.value();
        std::cout << "Квадратичний підйом: корінь a_" << k2 << " = " << res.root
                  << " (mod " << res.modulus << ") за " << res.iterations << " кроків\n";
        const auto check = math::HenselSolver::eval_poly(poly2, res.root, res.modulus);
        std::cout << "Перевірка: f(" << res.root << ") mod " << res.modulus << " = " << check
                  << " (успіх: " << (check == 0 ? "ТАК" : "НІ") << ")\n";
    }

    // Тест 3: Вироджений (кратний) корінь f(x) = x^2 - 1 ≡ 0 (mod 2)
    const std::vector<std::int64_t> poly3 = {-1, 0, 1};
    constexpr std::int64_t r3_init = 1;

    std::cout << "\n--- Тест 3: Особливий корінь f'(1) = 2 ≡ 0 (mod 2) ---\n";
    const auto res_singular = math::HenselSolver::lift_linear(poly3, 2, 3, r3_init);
    if (!res_singular.has_value()) {
        std::cout << "Особливий корінь виявлено: f'(r1) ≡ 0 (mod p), підйом відхилено коректно.\n";
    }

    return 0;
}
