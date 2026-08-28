#include <iostream>
#include <vector>
#include <queue>
#include <optional>
#include <span>
#include <cstdint>

namespace horn {

enum class SolutionStatus {
    Sat,
    Unsat
};

class HornSolver {
public:
    static constexpr int32_t VarNone = -1;

    explicit HornSolver(size_t num_vars)
        : num_vars_(num_vars), assignment_(num_vars, 0), body_adj_(num_vars) {}

    // Додати факт: ⊤ → head_var
    void add_fact(int32_t head_var) {
        add_clause({}, head_var);
    }

    // Додати правило: (body[0] ∧ body[1] ∧ ...) → head_var
    void add_rule(std::span<const int32_t> body, int32_t head_var) {
        add_clause(body, head_var);
    }

    // Додати негативне обмеження цілісності: (body[0] ∧ body[1] ∧ ...) → ⊥
    void add_constraint(std::span<const int32_t> body) {
        add_clause(body, VarNone);
    }

    // Розв'язати формулу за лінійний час O(N)
    SolutionStatus solve() {
        while (!prop_queue_.empty()) {
            int32_t u = prop_queue_.front();
            prop_queue_.pop();

            for (size_t clause_id : body_adj_[u]) {
                counts_[clause_id]--;

                if (counts_[clause_id] == 0) {
                    int32_t h = heads_[clause_id];
                    if (h == VarNone) {
                        return SolutionStatus::Unsat;
                    }
                    if (assignment_[h] == 0) {
                        assignment_[h] = 1;
                        prop_queue_.push(h);
                    }
                }
            }
        }
        return SolutionStatus::Sat;
    }

    [[nodiscard]] const std::vector<uint8_t>& model() const noexcept {
        return assignment_;
    }

private:
    void add_clause(std::span<const int32_t> body, int32_t head_var) {
        size_t clause_id = heads_.size();
        heads_.size();
        heads_.push_back(head_var);
        counts_.push_back(body.size());

        for (int32_t var : body) {
            body_adj_[var].push_back(clause_id);
        }

        if (body.empty() && head_var != VarNone) {
            if (assignment_[head_var] == 0) {
                assignment_[head_var] = 1;
                prop_queue_.push(head_var);
            }
        }
    }

    size_t num_vars_;
    std::vector<int32_t> heads_;
    std::vector<size_t> counts_;
    std::vector<std::vector<size_t>> body_adj_;
    std::vector<uint8_t> assignment_;
    std::queue<int32_t> prop_queue_;
};

} // namespace horn

int main() {
    using namespace horn;

    // Створюємо розв'язувач для 4 змінних (x0, x1, x2, x3)
    HornSolver solver(4);

    // Додаємо факти
    solver.add_fact(0); // x0 = 1
    solver.add_fact(3); // x3 = 1

    // Додаємо правила
    const int32_t r1[] = {0};
    solver.add_rule(r1, 1); // x0 → x1

    const int32_t r2[] = {1, 3};
    solver.add_rule(r2, 2); // (x1 ∧ x3) → x2

    // Додаємо обмеження
    const int32_t c1[] = {2, 0};
    solver.add_constraint(c1); // (x2 ∧ x0) → ⊥

    SolutionStatus result = solver.solve();

    if (result == SolutionStatus::Sat) {
        std::cout << "Результат: SAT (здійсненна). Мінімальна модель:\n";
        const auto& m = solver.model();
        for (size_t i = 0; i < m.size(); ++i) {
            std::cout << "  x" << i << " = " << static_cast<int>(m[i]) << "\n";
        }
    } else {
        std::cout << "Результат: UNSAT (суперечна база знань).\n";
    }

    return 0;
}
