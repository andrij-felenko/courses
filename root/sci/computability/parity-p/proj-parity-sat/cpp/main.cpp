#include <iostream>
#include <vector>
#include <cmath>
#include <numeric>
#include <span>
#include <memory>
#include <array>

class Formula {
public:
    using Literal = int; // >0 для позитивної змінної, <0 для заперечення
    using Clause = std::vector<Literal>;

    explicit Formula(size_t num_vars) : num_vars_(num_vars) {}

    void add_clause(std::span<const Literal> lits) {
        clauses_.emplace_back(lits.begin(), lits.end());
    }

    [[nodiscard]] size_t num_vars() const noexcept { return num_vars_; }
    [[nodiscard]] const std::vector<Clause>& clauses() const noexcept { return clauses_; }

private:
    size_t num_vars_;
    std::vector<Clause> clauses_;
};

class ParitySatSolver {
public:
    explicit ParitySatSolver(const Formula& formula)
        : formula_(formula), assignment_(formula.num_vars() + 1, 0) {}

    // Обчислює парність кількості розв'язків (0 = парна, 1 = непарна)
    [[nodiscard]] int solve_parity() {
        return solve_recursive(1);
    }

private:
    int solve_recursive(size_t var_idx) {
        if (var_idx > formula_.num_vars()) {
            return check_assignment() ? 1 : 0;
        }

        // Гілка 0
        assignment_[var_idx] = 0;
        int left = solve_recursive(var_idx + 1);

        // Гілка 1
        assignment_[var_idx] = 1;
        int right = solve_recursive(var_idx + 1);

        // Додавання за модулем 2 (XOR)
        return left ^ right;
    }

    [[nodiscard]] bool check_assignment() const {
        for (const auto& clause : formula_.clauses()) {
            bool clause_sat = false;
            for (int lit : clause) {
                size_t var = static_cast<size_t>(std::abs(lit));
                bool val = (assignment_[var] == 1);
                if (lit < 0) val = !val;
                if (val) {
                    clause_sat = true;
                    break;
                }
            }
            if (!clause_sat) return false;
        }
        return true;
    }

    const Formula& formula_;
    std::vector<int> assignment_;
};

int main() {
    Formula f(3);
    f.add_clause(std::array<int, 2>{1, 2});
    f.add_clause(std::array<int, 2>{-1, 3});
    f.add_clause(std::array<int, 2>{2, -3});

    ParitySatSolver solver(f);
    int parity = solver.solve_parity();

    std::cout << "Parity of satisfying assignments (mod 2): " << parity << '\n';
    std::cout << "Is odd: " << (parity == 1 ? "YES" : "NO") << '\n';

    return 0;
}
