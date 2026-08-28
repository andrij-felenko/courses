#include <iostream>
#include <vector>
#include <memory>
#include <span>
#include <string_view>

enum class Quantifier {
    Exists,
    Forall
};

struct Literal {
    int var;        // Індекс змінної (1-based)
    bool is_pos;    // true = x, false = ¬x
};

using Clause = std::vector<Literal>;

struct CNFFormula {
    std::vector<Clause> clauses;

    [[nodiscard]] bool evaluate(std::span<const bool> assignment) const {
        for (const auto& clause : clauses) {
            bool clause_sat = false;
            for (const auto& lit : clause) {
                const bool val = assignment[lit.var];
                if ((lit.is_pos && val) || (!lit.is_pos && !val)) {
                    clause_sat = true;
                    break;
                }
            }
            if (!clause_sat) {
                return false;
            }
        }
        return true;
    }
};

class TQBFEvaluator {
public:
    TQBFEvaluator(std::vector<Quantifier> quantifiers, CNFFormula cnf)
        : quantifiers_(std::move(quantifiers)), cnf_(std::move(cnf)) {}

    [[nodiscard]] bool evaluate() const {
        // Запитуємо O(N) пам'яті під виділені значення змінних
        std::vector<bool> assignment(quantifiers_.size() + 1, false);
        return evaluate_step(1, assignment);
    }

private:
    std::vector<Quantifier> quantifiers_;
    CNFFormula cnf_;

    bool evaluate_step(size_t depth, std::span<bool> assignment) const {
        if (depth > quantifiers_.size()) {
            return cnf_.evaluate(assignment);
        }

        const Quantifier q = quantifiers_[depth - 1];

        // Гілка 1: var = false
        assignment[depth] = false;
        const bool res_false = evaluate_step(depth + 1, assignment);

        // Оптимізація короткого замикання (Short-circuit evaluation)
        if (q == Quantifier::Exists && res_false) {
            return true;
        }
        if (q == Quantifier::Forall && !res_false) {
            return false;
        }

        // Гілка 2: var = true
        assignment[depth] = true;
        const bool res_true = evaluate_step(depth + 1, assignment);

        if (q == Quantifier::Exists) {
            return res_false || res_true;
        } else {
            return res_false && res_true;
        }
    }
};

int main() {
    // Приклад TQBF: ∃x₁ ∀x₂ ((x₁ ∨ x₂) ∧ (x₁ ∨ ¬x₂))
    std::vector<Quantifier> quants = { Quantifier::Exists, Quantifier::Forall };
    
    CNFFormula cnf;
    cnf.clauses = {
        { Literal{1, true}, Literal{2, true} },   // (x₁ ∨ x₂)
        { Literal{1, true}, Literal{2, false} }   // (x₁ ∨ ¬x₂)
    };

    TQBFEvaluator evaluator(std::move(quants), std::move(cnf));
    const bool result = evaluator.evaluate();

    std::cout << "Формула ∃x₁ ∀x₂ ((x₁ ∨ x₂) ∧ (x₁ ∨ ¬x₂)) є: "
              << (result ? "ІСТИННОЮ (True)" : "ХИБНОЮ (False)") << "\n";

    return 0;
}
