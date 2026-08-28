#include <iostream>
#include <unordered_map>
#include <cmath>
#include <optional>
#include <cstdint>
#include <vector>
#include <numeric>

namespace dlog {

// Клас для безпечної модульної арифметики (64-бітний модуль)
class ModularArithmetic {
public:
    static uint64_t mul(uint64_t a, uint64_t b, uint64_t mod) {
        return static_cast<uint64_t>((static_cast<__int128_t>(a) * b) % mod);
    }

    static uint64_t power(uint64_t base, uint64_t exp, uint64_t mod) {
        uint64_t result = 1;
        base %= mod;
        while (exp > 0) {
            if (exp & 1) {
                result = mul(result, base, mod);
            }
            base = mul(base, base, mod);
            exp >>= 1;
        }
        return result;
    }

    // Розширений алгоритм Евкліда для пошуку модульного оберненого (a^-1 mod mod)
    static std::optional<uint64_t> mod_inverse(uint64_t a, uint64_t mod) {
        int64_t t = 0, newt = 1;
        int64_t r = static_cast<int64_t>(mod), newr = static_cast<int64_t>(a);

        while (newr != 0) {
            int64_t quotient = r / newr;
            int64_t temp_t = t - quotient * newt;
            t = newt;
            newt = temp_t;

            int64_t temp_r = r - quotient * newr;
            r = newr;
            newr = temp_r;
        }

        if (r > 1) return std::nullopt; // Елемент не має оберненого
        if (t < 0) t += static_cast<int64_t>(mod);
        return static_cast<uint64_t>(t);
    }
};

// Результат обчислення логарифма
struct SolverResult {
    uint64_t exponent;
    uint64_t steps;
    bool found;
};

class DiscreteLogSolver {
public:
    // Алгоритм Shanks Baby-Step Giant-Step (BSGS)
    // Час: O(sqrt(N)), Пам'ять: O(sqrt(N))
    static SolverResult solve_bsgs(uint64_t g, uint64_t y, uint64_t p, uint64_t N) {
        uint64_t m = static_cast<uint64_t>(std::ceil(std::sqrt(static_cast<double>(N))));
        std::unordered_map<uint64_t, uint64_t> baby_steps;
        baby_steps.reserve(m);

        uint64_t cur = y % p;
        uint64_t steps_count = 0;

        // Kрок 1: Baby steps (зберігаємо y * g^j mod p для j in [0, m-1])
        for (uint64_t j = 0; j < m; ++j) {
            baby_steps[cur] = j;
            cur = ModularArithmetic::mul(cur, g, p);
            steps_count++;
        }

        // Крок 2: Giant steps (шукаємо (g^m)^i mod p)
        uint64_t factor = ModularArithmetic::power(g, m, p);
        cur = factor;

        for (uint64_t i = 1; i <= m; ++i) {
            steps_count++;
            auto it = baby_steps.find(cur);
            if (it != baby_steps.end()) {
                uint64_t j = it->second;
                uint64_t x = (i * m - j) % N;
                return SolverResult{x, steps_count, true};
            }
            cur = ModularArithmetic::mul(cur, factor, p);
        }

        return SolverResult{0, steps_count, false};
    }

    // Алгоритм Pollard's Rho для дискретного логарифмування
    // Час: O(sqrt(N)), Пам'ять: O(1)
    static SolverResult solve_pollard_rho(uint64_t g, uint64_t y, uint64_t p, uint64_t N) {
        struct State {
            uint64_t x; // поточний елемент групи w_k
            uint64_t a; // експонента g
            uint64_t b; // експонента y
        };

        auto next_state = [g, y, p, N](const State& st) -> State {
            switch (st.x % 3) {
                case 0: // Підмножина G1: x = x^2, a = 2a, b = 2b
                    return State{
                        ModularArithmetic::mul(st.x, st.x, p),
                        (st.a * 2) % N,
                        (st.b * 2) % N
                    };
                case 1: // Підмножина G2: x = x * g, a = a + 1, b = b
                    return State{
                        ModularArithmetic::mul(st.x, g, p),
                        (st.a + 1) % N,
                        st.b
                    };
                default: // Підмножина G3: x = x * y, a = a, b = b + 1
                    return State{
                        ModularArithmetic::mul(st.x, y, p),
                        st.a,
                        (st.b + 1) % N
                    };
            }
        };

        State tortoise{1, 0, 0};
        State hare = tortoise;
        uint64_t steps_count = 0;

        // Пошук колізії методом Флойда
        do {
            tortoise = next_state(tortoise);
            hare = next_state(next_state(hare));
            steps_count += 3;

            if (steps_count > 10 * N) { // Захист від безнадійного зациклення
                return SolverResult{0, steps_count, false};
            }
        } while (tortoise.x != hare.x);

        // Колізію знайдено: g^(a1) * y^(b1) = g^(a2) * y^(b2)
        // Звідси (b1 - b2) * x = (a2 - a1) mod N
        int64_t r_b = (static_cast<int64_t>(tortoise.b) - static_cast<int64_t>(hare.b)) % static_cast<int64_t>(N);
        if (r_b < 0) r_b += static_cast<int64_t>(N);

        int64_t r_a = (static_cast<int64_t>(hare.a) - static_cast<int64_t>(tortoise.a)) % static_cast<int64_t>(N);
        if (r_a < 0) r_a += static_cast<int64_t>(N);

        auto inv_b = ModularArithmetic::mod_inverse(static_cast<uint64_t>(r_b), N);
        if (!inv_b.has_value()) {
            // Колізія непридатна (НСД > 1), потрібно перезапустити з іншими початковими станами
            return SolverResult{0, steps_count, false};
        }

        uint64_t x = ModularArithmetic::mul(static_cast<uint64_t>(r_a), inv_b.value(), N);
        return SolverResult{x, steps_count, true};
    }
};

} // namespace dlog

int main() {
    uint64_t p = 10007;
    uint64_t g = 5;
    uint64_t N = p - 1;
    uint64_t secret_x = 1234;

    uint64_t y = dlog::ModularArithmetic::power(g, secret_x, p);

    std::cout << "=== Тестування розв'язувачів проблеми дискретного логарифма ===\n";
    std::cout << "Параметри: p = " << p << ", g = " << g << ", y = " << y << " (Секретне x = " << secret_x << ")\n\n";

    // Тест BSGS
    auto res_bsgs = dlog::DiscreteLogSolver::solve_bsgs(g, y, p, N);
    if (res_bsgs.found) {
        std::cout << "[BSGS] Успіх! Знайдено x = " << res_bsgs.exponent 
                  << " за " << res_bsgs.steps << " кроків.\n";
    } else {
        std::cout << "[BSGS] Помилка: логарифм не знайдено.\n";
    }

    // Тест Pollard Rho
    auto res_rho = dlog::DiscreteLogSolver::solve_pollard_rho(g, y, p, N);
    if (res_rho.found) {
        std::cout << "[Pollard Rho] Успіх! Знайдено x = " << res_rho.exponent 
                  << " за " << res_rho.steps << " кроків.\n";
    } else {
        std::cout << "[Pollard Rho] Не вдалося знайти з першої спроби (потрібен перезапуск).\n";
    }

    return 0;
}
