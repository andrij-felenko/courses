#include <iostream>
#include <vector>
#include <optional>
#include <numeric>
#include <cstdint>
#include <stdexcept>

class HenselSolver {
public:
    static std::int64_t mod_inverse(std::int64_t a, std::int64_t m) {
        std::int64_t m0 = m, y = 0, x = 1;
        if (m == 1) return 0;
        a = (a % m + m) % m;
        while (a > 1) {
            std::int64_t q = a / m;
            std::int64_t t = m;
            m = a % m; a = t;
            t = y;
            y = x - q * y;
            x = t;
        }
        return (x < 0) ? x + m0 : x;
    }

    /* Оцінка значення многочлена за допомогою схеми Горнера */
    static std::int64_t eval_poly(const std::vector<std::int64_t>& poly, std::int64_t x, std::int64_t mod) {
        std::int64_t res = 0;
        for (auto it = poly.rbegin(); it != poly.rend(); ++it) {
            res = (res * x + *it) % mod;
            if (res < 0) res += mod;
        }
        return res;
    }

    /* Оцінка значення похідної за допомогою схеми Горнера */
    static std::int64_t eval_derivative(const std::vector<std::int64_t>& poly, std::int64_t x, std::int64_t mod) {
        if (poly.size() <= 1) return 0;
        std::int64_t res = 0;
        for (std::size_t i = poly.size() - 1; i >= 1; --i) {
            std::int64_t coeff = (poly[i] * static_cast<std::int64_t>(i)) % mod;
            res = (res * x + coeff) % mod;
            if (res < 0) res += mod;
        }
        return res;
    }

    /* Квадратичний підйом Гензеля (подвоєння степеня p на кожному кроці) */
    static std::optional<std::int64_t> lift_quadratic(
        const std::vector<std::int64_t>& poly,
        std::int64_t p,
        std::size_t target_k,
        std::int64_t initial_root) 
    {
        std::int64_t root = (initial_root % p + p) % p;
        std::int64_t f_prime = eval_derivative(poly, root, p);
        if (f_prime % p == 0) {
            return std::nullopt; /* Особливий корінь */
        }

        std::int64_t current_mod = p;
        while (current_mod < power(p, target_k)) {
            std::int64_t next_mod = current_mod * current_mod;
            std::int64_t f_val = eval_poly(poly, root, next_mod);
            std::int64_t df_val = eval_derivative(poly, root, next_mod);
            
            std::int64_t inv_df = mod_inverse(df_val, next_mod);
            std::int64_t correction = (f_val * inv_df) % next_mod;
            root = (root - correction + next_mod) % next_mod;
            
            current_mod = next_mod;
        }

        std::int64_t target_mod = power(p, target_k);
        return (root % target_mod + target_mod) % target_mod;
    }

private:
    static std::int64_t power(std::int64_t base, std::size_t exp) {
        std::int64_t res = 1;
        for (std::size_t i = 0; i < exp; ++i) res *= base;
        return res;
    }
};

int main() {
    /* Рівняння x^2 - 7 = 0 (mod 3^5) */
    std::vector<std::int64_t> poly = {-7, 0, 1};
    std::int64_t p = 3;
    std::size_t target_k = 5;
    std::int64_t r1 = 1;

    auto result = HenselSolver::lift_quadratic(poly, p, target_k, r1);
    if (result.has_value()) {
        std::cout << "Kvadratychnyy pidyom mod 3^5 (243): " << result.value() << "\n";
        std::int64_t check = HenselSolver::eval_poly(poly, result.value(), 243);
        std::cout << "Perevirka f(root) mod 243 = " << check << "\n";
    } else {
        std::cout << "Pidyom nemozhlyvyy (osoblyvyy korin)\n";
    }

    return 0;
}
