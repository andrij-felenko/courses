#include <iostream>
#include <vector>
#include <cmath>
#include <optional>
#include <algorithm>

enum class LitState { Unassigned, True, False };

struct Clause {
    std::vector<int> lits; // >0 для x_i, <0 для NOT x_i
};

class DpllSolver {
public:
    DpllSolver(int num_vars, std::vector<Clause> clauses)
        : num_vars_(num_vars), clauses_(std::move(clauses)), val_(num_vars + 1, LitState::Unassigned) {}

    struct SolveResult {
        bool is_sat;
        std::vector<bool> assignment;
        long long decision_count;
    };

    SolveResult solve() {
        decision_count_ = 0;
        bool sat = run_dpll();
        std::vector<bool> assign(num_vars_ + 1, false);
        if (sat) {
            for (int i = 1; i <= num_vars_; ++i) {
                assign[i] = (val_[i] == LitState::True);
            }
        }
        return {sat, assign, decision_count_};
    }

private:
    int num_vars_;
    std::vector<Clause> clauses_;
    std::vector<LitState> val_;
    long long decision_count_ = 0;

    int eval_lit(int lit) const {
        int var = std::abs(lit);
        if (val_[var] == LitState::Unassigned) return 0;
        bool is_true = (val_[var] == LitState::True);
        return (lit > 0) ? (is_true ? 1 : -1) : (is_true ? -1 : 1);
    }

    bool unit_propagation() {
        bool changed = true;
        while (changed) {
            changed = false;
            for (const auto& clause : clauses_) {
                int unassigned_lit = 0;
                int unassigned_cnt = 0;
                bool satisfied = false;

                for (int lit : clause.lits) {
                    int ev = eval_lit(lit);
                    if (ev == 1) { satisfied = true; break; }
                    if (ev == 0) { unassigned_cnt++; unassigned_lit = lit; }
                }

                if (satisfied) continue;
                if (unassigned_cnt == 0) return false; // UNSAT conflict

                if (unassigned_cnt == 1) {
                    int var = std::abs(unassigned_lit);
                    val_[var] = (unassigned_lit > 0) ? LitState::True : LitState::False;
                    changed = true;
                }
            }
        }
        return true;
    }

    void pure_literal_elimination() {
        std::vector<int> pos_cnt(num_vars_ + 1, 0);
        std::vector<int> neg_cnt(num_vars_ + 1, 0);

        for (const auto& clause : clauses_) {
            bool sat = false;
            for (int lit : clause.lits) {
                if (eval_lit(lit) == 1) { sat = true; break; }
            }
            if (sat) continue;

            for (int lit : clause.lits) {
                if (eval_lit(lit) == 0) {
                    if (lit > 0) pos_cnt[lit]++;
                    else neg_cnt[-lit]++;
                }
            }
        }

        for (int v = 1; v <= num_vars_; ++v) {
            if (val_[v] == LitState::Unassigned) {
                if (pos_cnt[v] > 0 && neg_cnt[v] == 0) val_[v] = LitState::True;
                else if (neg_cnt[v] > 0 && pos_cnt[v] == 0) val_[v] = LitState::False;
            }
        }
    }

    bool is_satisfied() const {
        for (const auto& clause : clauses_) {
            bool clause_sat = false;
            for (int lit : clause.lits) {
                if (eval_lit(lit) == 1) { clause_sat = true; break; }
            }
            if (!clause_sat) return false;
        }
        return true;
    }

    bool run_dpll() {
        decision_count_++;

        if (!unit_propagation()) return false;
        pure_literal_elimination();

        if (is_satisfied()) return true;

        int next_var = 0;
        for (int v = 1; v <= num_vars_; ++v) {
            if (val_[v] == LitState::Unassigned) { next_var = v; break; }
        }
        if (next_var == 0) return is_satisfied();

        auto backup_val = val_;

        // Branch 1: Try True
        val_[next_var] = LitState::True;
        if (run_dpll()) return true;

        // Branch 2: Try False
        val_ = backup_val;
        val_[next_var] = LitState::False;
        return run_dpll();
    }
};

int main() {
    std::cout << "=== Об'єктно-орієнтований DPLL SAT-соловер (C++) ===\n";

    std::vector<Clause> formula = {
        Clause{{1, 2}},
        Clause{{-1, 3}},
        Clause{{-2, 4}},
        Clause{{-3, -4}},
        Clause{{1, -4}}
    };

    DpllSolver solver(4, formula);
    auto res = solver.solve();

    if (res.is_sat) {
        std::cout << "Результат: SAT\nПризначення:\n";
        for (int i = 1; i <= 4; ++i) {
            std::cout << "  x" << i << " = " << (res.assignment[i] ? "True" : "False") << "\n";
        }
    } else {
        std::cout << "Результат: UNSAT\n";
    }
    std::cout << "Кількість рекурсивних кроків: " << res.decision_count << "\n";

    return 0;
}
