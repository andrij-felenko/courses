// qsat_solver.cpp — Ідіоматичний розв'язувач QBF сучасним C++20 (RAII, std::vector, std::span)
#include <iostream>
#include <vector>
#include <cmath>
#include <optional>
#include <span>

enum class Quantifier {
    Exists,
    Forall
};

struct Variable {
    int id;
    Quantifier type;
};

class Clause {
public:
    std::vector<int> literals;

    [[nodiscard]] std::optional<bool> evaluate(std::span<const int> values) const {
        bool has_unassigned = false;
        for (int lit : literals) {
            int var = std::abs(lit);
            int val = values[var];
            if (val == -1) {
                has_unassigned = true;
            } else {
                bool is_positive = (lit > 0);
                if ((is_positive && val == 1) || (!is_positive && val == 0)) {
                    return true; // Диз'юнкт істинний
                }
            }
        }
        if (has_unassigned) return std::nullopt; // Ще не визначено
        return false; // Диз'юнкт хибний
    }
};

class QBFFormula {
public:
    size_t num_vars{0};
    std::vector<Variable> quantifiers;
    std::vector<Clause> clauses;

    [[nodiscard]] std::optional<bool> evaluate(std::span<const int> values) const {
        bool has_undefined = false;
        for (const auto& clause : clauses) {
            auto res = clause.evaluate(values);
            if (res == false) return false;
            if (!res.has_value()) has_undefined = true;
        }
        if (has_undefined) return std::nullopt;
        return true;
    }

    [[nodiscard]] bool solve() const {
        std::vector<int> values(num_vars + 1, -1);
        return solve_recursive(0, values);
    }

private:
    bool solve_recursive(size_t quant_idx, std::vector<int>& values) const {
        auto status = evaluate(values);
        if (status.has_value()) {
            return status.value();
        }
        if (quant_idx >= quantifiers.size()) {
            return false;
        }

        const auto& [var_id, qtype] = quantifiers[quant_idx];

        if (qtype == Quantifier::Exists) {
            // Квантор ∃: АБО двох гілок
            values[var_id] = 0;
            if (solve_recursive(quant_idx + 1, values)) {
                values[var_id] = -1;
                return true;
            }
            values[var_id] = 1;
            bool res = solve_recursive(quant_idx + 1, values);
            values[var_id] = -1;
            return res;
        } else {
            // Квантор ∀: І двох гілок (з раннім відсіканням)
            values[var_id] = 0;
            if (!solve_recursive(quant_idx + 1, values)) {
                values[var_id] = -1;
                return false; // Раннє відсікання
            }
            values[var_id] = 1;
            bool res = solve_recursive(quant_idx + 1, values);
            values[var_id] = -1;
            return res;
        }
    }
};

int main() {
    // Формула: ∃ x1 ∀ y2 [ (x1 OR y2) AND (x1 OR NOT y2) ]
    QBFFormula formula;
    formula.num_vars = 2;
    formula.quantifiers = {
        {1, Quantifier::Exists},
        {2, Quantifier::Forall}
    };
    formula.clauses = {
        Clause{{1, 2}},   // x1 OR y2
        Clause{{1, -2}}   // x1 OR NOT y2
    };

    bool is_satisfiable = formula.solve();
    std::cout << "Результат оцінки ∃x1 ∀y2 [(x1 OR y2) AND (x1 OR !y2)]: "
              << (is_satisfiable ? "TRUE (ІСТИНА)" : "FALSE (ХИБА)") << '\n';

    return 0;
}
