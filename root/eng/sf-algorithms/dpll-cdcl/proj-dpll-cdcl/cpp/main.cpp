#include <iostream>
#include <vector>
#include <cmath>
#include <optional>
#include <memory>
#include <algorithm>
#include <span>

enum class LBool : int8_t {
    Undefined = -1,
    False = 0,
    True = 1
};

struct Clause {
    std::vector<int> lits;
    size_t w1{0};
    size_t w2{0};
    int lbd{0};

    explicit Clause(std::span<const int> literals)
        : lits(literals.begin(), literals.end()) {
        if (lits.size() > 1) {
            w2 = 1;
        }
    }
};

class CDCLSolver {
public:
    explicit CDCLSolver(size_t num_vars)
        : num_vars_(num_vars),
          assigns_(num_vars + 1, LBool::Undefined),
          levels_(num_vars + 1, -1),
          reasons_(num_vars + 1, nullptr),
          activity_(num_vars + 1, 0.0) {}

    void add_clause(std::span<const int> literals) {
        clauses_.push_back(std::make_unique<Clause>(literals));
    }

    [[nodiscard]] LBool lit_value(int lit) const noexcept {
        const int var = std::abs(lit);
        const LBool val = assigns_[var];
        if (val == LBool::Undefined) return LBool::Undefined;
        return (lit > 0) ? val : (val == LBool::True ? LBool::False : LBool::True);
    }

    void assign(int lit, Clause* reason = nullptr) {
        const int var = std::abs(lit);
        const LBool val = (lit > 0) ? LBool::True : LBool::False;
        assigns_[var] = val;
        levels_[var] = current_level_;
        reasons_[var] = reason;
        trail_.push_back({var, current_level_});
    }

    Clause* bcp() {
        for (auto& clause_ptr : clauses_) {
            Clause& c = *clause_ptr;
            size_t false_count = 0;
            int undef_lit = 0;
            size_t undef_count = 0;
            bool satisfied = false;

            for (int lit : c.lits) {
                LBool val = lit_value(lit);
                if (val == LBool::True) {
                    satisfied = true;
                    break;
                }
                if (val == LBool::False) {
                    false_count++;
                } else {
                    undef_count++;
                    undef_lit = lit;
                }
            }

            if (satisfied) continue;

            if (false_count == c.lits.size()) {
                return &c; // Conflict!
            }

            if (undef_count == 1) {
                assign(undef_lit, &c);
            }
        }
        return nullptr;
    }

    void backtrack(int target_level) {
        while (!trail_.empty() && trail_.back().level > target_level) {
            int var = trail_.back().var;
            assigns_[var] = LBool::Undefined;
            levels_[var] = -1;
            reasons_[var] = nullptr;
            trail_.pop_back();
        }
        current_level_ = target_level;
    }

    void bump_var_activity(int var) {
        activity_[var] += var_inc_;
        if (activity_[var] > 1e100) {
            for (size_t i = 1; i <= num_vars_; ++i) {
                activity_[i] *= 1e-100;
            }
            var_inc_ *= 1e-100;
        }
    }

    int pick_decision_variable() {
        int best_var = 0;
        double max_act = -1.0;
        for (size_t i = 1; i <= num_vars_; ++i) {
            if (assigns_[i] == LBool::Undefined) {
                if (activity_[i] > max_act) {
                    max_act = activity_[i];
                    best_var = static_cast<int>(i);
                }
            }
        }
        return best_var;
    }

    bool solve() {
        while (true) {
            Clause* conflict = bcp();
            if (conflict != nullptr) {
                if (current_level_ == 0) return false; // UNSAT
                backtrack(current_level_ - 1);
                continue;
            }

            int next_var = pick_decision_variable();
            if (next_var == 0) return true; // SAT

            current_level_++;
            assign(next_var, nullptr);
        }
    }

    [[nodiscard]] LBool get_value(size_t var) const {
        return assigns_.at(var);
    }

private:
    struct TrailEntry {
        int var;
        int level;
    };

    size_t num_vars_;
    std::vector<std::unique_ptr<Clause>> clauses_;
    std::vector<LBool> assigns_;
    std::vector<int> levels_;
    std::vector<Clause*> reasons_;
    std::vector<double> activity_;
    std::vector<TrailEntry> trail_;
    int current_level_{0};
    double var_inc_{1.0};
};

int main() {
    CDCLSolver solver(3);

    // F = (x₁ ∨ x₂) ∧ (¬x₁ ∨ x₃) ∧ (¬x₂ ∨ ¬x₃)
    const int c1[] = {1, 2};
    const int c2[] = {-1, 3};
    const int c3[] = {-2, -3};

    solver.add_clause(c1);
    solver.add_clause(c2);
    solver.add_clause(c3);

    if (solver.solve()) {
        std::cout << "SAT! Assigns: x1=" << static_cast<int>(solver.get_value(1))
                  << ", x2=" << static_cast<int>(solver.get_value(2))
                  << ", x3=" << static_cast<int>(solver.get_value(3)) << "\n";
    } else {
        std::cout << "UNSAT!\n";
    }

    return 0;
}
