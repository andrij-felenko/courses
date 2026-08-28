#include <iostream>
#include <tuple>
#include <vector>
#include <optional>
#include <cmath>
#include <unordered_set>
#include <algorithm>

// Розширений алгоритм Евкліда (C++17 std::tuple)
std::tuple<long long, long long, long long> extended_gcd(long long a, long long b) {
    if (b == 0) {
        if (a < 0) return {-a, -1, 0};
        return {a, 1, 0};
    }
    auto [d, x1, y1] = extended_gcd(b, a % b);
    long long x = y1;
    long long y = x1 - (a / b) * y1;
    return {d, x, y};
}

class LinearDiophantineSolver {
private:
    long long a, b, c;
    long long d, x0, y0;

public:
    LinearDiophantineSolver(long long a_, long long b_, long long c_)
        : a(a_), b(b_), c(c_) {
        auto [g, x_gcd, y_gcd] = extended_gcd(std::abs(a), std::abs(b));
        d = g;
        x0 = (a < 0) ? -x_gcd : x_gcd;
        y0 = (b < 0) ? -y_gcd : y_gcd;
    }

    bool is_solvable() const {
        if (a == 0 && b == 0) return c == 0;
        return c % d == 0;
    }

    std::optional<std::pair<long long, long long>> particular_solution() const {
        if (!is_solvable()) return std::nullopt;
        long long scale = c / d;
        return std::make_pair(x0 * scale, y0 * scale);
    }

    std::vector<std::pair<long long, long long>> non_negative_solutions() const {
        if (!is_solvable()) return {};
        
        auto part = particular_solution();
        if (!part) return {};
        auto [x1, y1] = *part;

        long long step_x = b / d;
        long long step_y = -a / d;

        if (step_x == 0 && step_y == 0) {
            if (x1 >= 0 && y1 >= 0) return {{x1, y1}};
            return {};
        }

        long long t_min = -1e18;
        long long t_max = 1e18;

        if (step_x > 0) {
            t_min = std::max(t_min, (long long)std::ceil(-(double)x1 / step_x));
        } else if (step_x < 0) {
            t_max = std::min(t_max, (long long)std::floor(-(double)x1 / step_x));
        }

        if (step_y > 0) {
            t_min = std::max(t_min, (long long)std::ceil(-(double)y1 / step_y));
        } else if (step_y < 0) {
            t_max = std::min(t_max, (long long)std::floor(-(double)y1 / step_y));
        }

        if (t_min > t_max) return {};

        std::vector<std::pair<long long, long long>> result;
        for (long long t = t_min; t <= t_max; ++t) {
            result.push_back({x1 + step_x * t, y1 + step_y * t});
        }
        return result;
    }
};

// Детектор модульних перешкод
std::optional<int> find_modular_obstruction(int a, int b, int c, int max_mod = 100) {
    for (int m = 2; m <= max_mod; ++m) {
        std::vector<int> squares;
        for (int x = 0; x < m; ++x) {
            squares.push_back((x * x) % m);
        }
        
        std::vector<bool> reachable(m, false);
        for (int sq1 : squares) {
            for (int sq2 : squares) {
                int val = (a * sq1 + b * sq2) % m;
                if (val < 0) val += m;
                reachable[val] = true;
            }
        }
        
        int target = c % m;
        if (target < 0) target += m;
        
        if (!reachable[target]) {
            return m;
        }
    }
    return std::nullopt;
}

int main() {
    std::cout << "=== Діофантів розв'язник (C++17) ===\n";
    LinearDiophantineSolver solver(5, 8, 43);
    std::cout << "Рівняння 5x + 8y = 43 розв'язне? " << (solver.is_solvable() ? "Так" : "Ні") << "\n";
    
    auto part = solver.particular_solution();
    if (part) {
        std::cout << "Частинний розв'язок: (" << part->first << ", " << part->second << ")\n";
    }

    auto non_neg = solver.non_negative_solutions();
    std::cout << "Невід'ємні розв'язки:\n";
    for (auto [x, y] : non_neg) {
        std::cout << "  x = " << x << ", y = " << y << "\n";
    }

    std::cout << "\n=== Пошук модульних перешкод ===\n";
    auto mod_obs = find_modular_obstruction(1, -3, 2);
    if (mod_obs) {
        std::cout << "Рівняння x² - 3y² = 2 має модульну перешкоду: mod " << *mod_obs << "\n";
    }

    return 0;
}
