#include <iostream>
#include <vector>
#include <cmath>
#include <cstdint>
#include <optional>

/* Клас ідіоматичного представлення КНФ-формули в C++ */
class CNFFormula {
public:
    struct Clause {
        std::vector<int> lits; // +1 для x1, -1 для NOT x1
    };

    size_t var_count;
    std::vector<Clause> clauses;

    CNFFormula(size_t vars) : var_count(vars) {}

    void add_clause(std::initializer_list<int> lits) {
        clauses.push_back(Clause{std::vector<int>(lits)});
    }

    /* Оцінка всієї формули при частковому призначення змінних */
    int evaluate(const std::vector<int8_t>& assignment) const {
        bool has_undef = false;
        for (const auto& clause : clauses) {
            bool clause_sat = false;
            bool clause_undef = false;

            for (int lit : clause.lits) {
                size_t var_idx = static_cast<size_t>(std::abs(lit) - 1);
                int8_t val = assignment[var_idx];

                if (val == -1) {
                    clause_undef = true;
                } else if ((lit > 0 && val == 1) || (lit < 0 && val == 0)) {
                    clause_sat = true;
                    break;
                }
            }

            if (!clause_sat && !clause_undef) {
                return 0; // Диз'юнкт хибний -> формула хибна
            }
            if (!clause_sat && clause_undef) {
                has_undef = true;
            }
        }
        return has_undef ? -1 : 1;
    }
};

/* Клас розв'язувача MAJSAT з використанням RAII та стану */
class MAJSATSolver {
public:
    struct Result {
        uint64_t sat_count;
        uint64_t total_paths;
        bool is_majority;
    };

    static Result solve(const CNFFormula& formula) {
        std::vector<int8_t> assignment(formula.var_count, -1);
        uint64_t total_paths = 1ULL << formula.var_count;
        uint64_t threshold = total_paths / 2;

        uint64_t sat_count = count_recursive(formula, 0, assignment);
        return Result{sat_count, total_paths, sat_count > threshold};
    }

private:
    static uint64_t count_recursive(const CNFFormula& formula, size_t var_idx, std::vector<int8_t>& assignment) {
        int status = formula.evaluate(assignment);

        if (status == 0) {
            return 0; // Раннє відтинання хибної гілки
        }

        if (var_idx == formula.var_count) {
            return (status == 1) ? 1ULL : 0ULL;
        }

        if (status == 1) {
            // Усі диз'юнкти задоволено -> усі 2^(N - var_idx) нащадків будуть виконуючими
            return 1ULL << (formula.var_count - var_idx);
        }

        // Гілка 0
        assignment[var_idx] = 0;
        uint64_t count_0 = count_recursive(formula, var_idx + 1, assignment);

        // Гілка 1
        assignment[var_idx] = 1;
        uint64_t count_1 = count_recursive(formula, var_idx + 1, assignment);

        // Відновлення стану
        assignment[var_idx] = -1;

        return count_0 + count_1;
    }
};

int main() {
    // Створюємо формулу: (x1 OR x2) AND (NOT x1 OR x3)
    CNFFormula formula(3);
    formula.add_clause({1, 2});
    formula.add_clause({-1, 3});

    auto result = MAJSATSolver::solve(formula);

    std::cout << "Кількість змінних: " << formula.var_count 
              << " (всього гілок: " << result.total_paths << ")\n";
    std::cout << "Кількість виконуючих наборів N_sat: " << result.sat_count << "\n";
    std::cout << "Поріг більшості (> " << (result.total_paths / 2) << "): "
              << (result.is_majority ? "ТАК (належить до MAJSAT)" : "НІ (не належить до MAJSAT)") << "\n";

    return 0;
}
