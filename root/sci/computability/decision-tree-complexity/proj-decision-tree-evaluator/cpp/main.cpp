// C++ Implementation: Decision Tree Complexity Analyzer
#include <iostream>
#include <vector>
#include <numeric>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <optional>
#include <bit>

class BooleanFunction {
public:
    explicit BooleanFunction(size_t num_vars, std::vector<uint8_t> truth_table)
        : n_(num_vars), table_(std::move(truth_table)) {
        if (table_.size() != (1ULL << n_)) {
            throw std::invalid_argument("Truth table size must equal 2^n");
        }
    }

    [[nodiscard]] size_t num_vars() const noexcept { return n_; }
    [[nodiscard]] uint8_t evaluate(uint32_t x) const { return table_.at(x); }

    // Перевірка константності на підпросторі
    [[nodiscard]] std::optional<uint8_t> get_constant_value(uint32_t fixed_mask, uint32_t fixed_vals) const {
        std::optional<uint8_t> first_val;
        const size_t total = table_.size();

        for (size_t x = 0; x < total; ++x) {
            if ((x & fixed_mask) == fixed_vals) {
                uint8_t val = table_[x];
                if (!first_val.has_value()) {
                    first_val = val;
                } else if (val != *first_val) {
                    return std::nullopt; // Не константа
                }
            }
        }
        return first_val;
    }

    // Обчислення чутливості s(f)
    [[nodiscard]] size_t sensitivity() const {
        size_t max_s = 0;
        const size_t total = table_.size();

        for (size_t x = 0; x < total; ++x) {
            size_t current_s = 0;
            for (size_t i = 0; i < n_; ++i) {
                size_t neighbor = x ^ (1ULL << i);
                if (table_[neighbor] != table_[x]) {
                    ++current_s;
                }
            }
            max_s = std::max(max_s, current_s);
        }
        return max_s;
    }

    // Обчислення складності сертифікатів C(f)
    [[nodiscard]] size_t certificate_complexity() const {
        size_t max_cert = 0;
        const size_t total = table_.size();

        for (size_t x = 0; x < total; ++x) {
            const uint8_t target_val = table_[x];
            size_t min_size_for_x = n_;

            for (uint32_t mask = 1; mask < (1U << n_); ++mask) {
                size_t size = std::popcount(mask);
                if (size >= min_size_for_x) continue;

                uint32_t fixed_vals = x & mask;
                auto const_opt = get_constant_value(mask, fixed_vals);
                if (const_opt.has_value() && *const_opt == target_val) {
                    min_size_for_x = size;
                }
            }
            max_cert = std::max(max_cert, min_size_for_x);
        }
        return max_cert;
    }

    // Рекурсивне обчислення D(f) через дерево рішень
    [[nodiscard]] size_t decision_tree_complexity() const {
        return solve_D(0, 0);
    }

private:
    size_t solve_D(uint32_t fixed_mask, uint32_t fixed_vals) const {
        auto const_opt = get_constant_value(fixed_mask, fixed_vals);
        if (const_opt.has_value()) {
            return 0;
        }

        size_t min_worst_depth = n_ + 1;

        for (size_t i = 0; i < n_; ++i) {
            if (!(fixed_mask & (1U << i))) {
                uint32_t next_mask = fixed_mask | (1U << i);

                size_t depth0 = solve_D(next_mask, fixed_vals);
                size_t depth1 = solve_D(next_mask, fixed_vals | (1U << i));

                size_t worst = 1 + std::max(depth0, depth1);
                min_worst_depth = std::min(min_worst_depth, worst);
            }
        }
        return min_worst_depth;
    }

    size_t n_;
    std::vector<uint8_t> table_;
};

int main() {
    // Функція більшості MAJ3 для n = 3
    std::vector<uint8_t> maj3_table(8);
    for (uint32_t x = 0; x < 8; ++x) {
        maj3_table[x] = (std::popcount(x) >= 2) ? 1 : 0;
    }

    BooleanFunction maj3(3, maj3_table);

    std::cout << "=== Аналіз складності функції MAJ(x1, x2, x3) ===\n";
    std::cout << "Чутливість s(MAJ): " << maj3.sensitivity() << "\n";
    std::cout << "Складність сертифікатів C(MAJ): " << maj3.certificate_complexity() << "\n";
    std::cout << "Детермінована складність D(MAJ): " << maj3.decision_tree_complexity() << "\n";

    return 0;
}
