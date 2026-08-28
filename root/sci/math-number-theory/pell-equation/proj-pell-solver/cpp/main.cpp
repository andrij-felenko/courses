#include <iostream>
#include <vector>
#include <optional>
#include <cmath>
#include <cstdint>
#include <limits>

struct PellSolution {
    std::uint64_t x;
    std::uint64_t y;
};

// Клас розв'язувача рівняння Пелля мовою C++ (RAII, безпечна арифметика, std::optional)
class PellSolver {
public:
    static std::optional<PellSolution> solve(std::uint64_t d) {
        const std::uint64_t a0 = static_cast<std::uint64_t>(std::sqrt(d));
        if (a0 * a0 == d) {
            return std::nullopt; // Параметр d є точним квадратом
        }

        std::uint64_t m = 0;
        std::uint64_t d_val = 1;
        std::uint64_t a = a0;

        std::uint64_t p_prev1 = 1;
        std::uint64_t p_curr = a0;

        std::uint64_t q_prev1 = 0;
        std::uint64_t q_curr = 1;

        while (true) {
            // Безпечна перевірка умови p^2 - d*q^2 == 1
            if (p_curr <= std::numeric_limits<std::uint64_t>::max() / p_curr &&
                q_curr <= std::numeric_limits<std::uint64_t>::max() / q_curr) {
                
                const std::uint64_t p2 = p_curr * p_curr;
                const std::uint64_t q2 = q_curr * q_curr;
                if (q2 <= (std::numeric_limits<std::uint64_t>::max() - 1) / d) {
                    if (p2 == 1 + d * q2) {
                        return PellSolution{p_curr, q_curr};
                    }
                }
            }

            // Обчислення наступного кроку неперервного дробу
            m = d_val * a - m;
            d_val = (d - m * m) / d_val;
            a = (a0 + m) / d_val;

            // Безпечна перевірка переповнення перед множенням та додаванням
            if (a > 0 && (p_curr > (std::numeric_limits<std::uint64_t>::max() - p_prev1) / a ||
                          q_curr > (std::numeric_limits<std::uint64_t>::max() - q_prev1) / a)) {
                return std::nullopt; // Переповнення типу uint64_t (потрібен BigInt)
            }

            const std::uint64_t p_next = a * p_curr + p_prev1;
            const std::uint64_t q_next = a * q_curr + q_prev1;

            p_prev1 = p_curr;
            p_curr = p_next;

            q_prev1 = q_curr;
            q_curr = q_next;
        }
    }
};

int main() {
    const std::vector<std::uint64_t> test_cases = {2, 3, 5, 7, 13, 61, 67, 109};

    for (std::uint64_t d : test_cases) {
        if (auto sol = PellSolver::solve(d)) {
            std::cout << "d = " << d << ": x = " << sol->x << ", y = " << sol->y << '\n';
        } else {
            std::cout << "d = " << d << ": розв'язок перевищує 64 біти або d є квадратом\n";
        }
    }

    return 0;
}
