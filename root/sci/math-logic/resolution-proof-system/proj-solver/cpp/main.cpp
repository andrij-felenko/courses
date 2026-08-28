#include <iostream>
#include <vector>
#include <algorithm>
#include <set>
#include <optional>
#include <cmath>
#include <string>

// Опис типу літерала (ціле число зі знаком: +v для x_v, -v для ¬x_v)
using Literal = int;

// Клас диз'юнкта з автоматичною нормалізацією та RAII
class Clause {
private:
    std::vector<Literal> lits_;
    bool is_tautology_{false};

    void normalize() {
        if (lits_.empty()) return;
        
        std::sort(lits_.begin(), lits_.end(), [](Literal a, Literal b) {
            if (std::abs(a) != std::abs(b)) return std::abs(a) < std::abs(b);
            return a < b;
        });

        std::vector<Literal> cleaned;
        for (size_t i = 0; i < lits_.size(); ++i) {
            if (i > 0 && lits_[i] == lits_[i - 1]) continue;
            if (i > 0 && lits_[i] == -lits_[i - 1]) {
                is_tautology_ = true;
                lits_.clear();
                return;
            }
            cleaned.push_back(lits_[i]);
        }
        lits_ = std::move(cleaned);
    }

public:
    Clause() = default;
    explicit Clause(std::vector<Literal> lits) : lits_(std::move(lits)) {
        normalize();
    }

    [[nodiscard]] bool empty() const { return lits_.empty() && !is_tautology_; }
    [[nodiscard]] bool is_tautology() const { return is_tautology_; }
    [[nodiscard]] size_t size() const { return lits_.size(); }
    [[nodiscard]] const std::vector<Literal>& literals() const { return lits_; }

    [[nodiscard]] bool contains(Literal l) const {
        return std::binary_search(lits_.begin(), lits_.end(), l, [](Literal a, Literal b) {
            if (std::abs(a) != std::abs(b)) return std::abs(a) < std::abs(b);
            return a < b;
        });
    }

    bool operator==(const Clause& other) const {
        return lits_ == other.lits_ && is_tautology_ == other.is_tautology_;
    }

    bool operator<(const Clause& other) const {
        return lits_ < other.lits_;
    }

    [[nodiscard]] std::string to_string() const {
        if (empty()) return "⊥";
        if (is_tautology_) return "⊤ (Tautology)";
        std::string s = "(";
        for (size_t i = 0; i < lits_.size(); ++i) {
            s += (lits_[i] > 0 ? "x" + std::to_string(lits_[i]) : "¬x" + std::to_string(-lits_[i]));
            if (i + 1 < lits_.size()) s += " ∨ ";
        }
        s += ")";
        return s;
    }
};

// Функція резолюційного виводу двох дизюнктів за змінною pivot
std::optional<Clause> resolve(const Clause& c1, const Clause& c2, int pivot) {
    bool c1_pos = c1.contains(pivot);
    bool c1_neg = c1.contains(-pivot);
    bool c2_pos = c2.contains(pivot);
    bool c2_neg = c2.contains(-pivot);

    if (!((c1_pos && c2_neg) || (c1_neg && c2_pos))) {
        return std::nullopt; // Резолюція неможлива
    }

    std::vector<Literal> res_lits;
    for (Literal l : c1.literals()) {
        if (std::abs(l) != pivot) res_lits.push_back(l);
    }
    for (Literal l : c2.literals()) {
        if (std::abs(l) != pivot) res_lits.push_back(l);
    }

    Clause res(std::move(res_lits));
    if (res.is_tautology()) return std::nullopt;
    return res;
}

// Двигун резолюційного спростування
class ResolutionSolver {
private:
    std::set<Clause> clause_db_;
    int num_vars_{0};

public:
    explicit ResolutionSolver(int num_vars) : num_vars_(num_vars) {}

    void add_clause(Clause c) {
        if (!c.is_tautology()) {
            clause_db_.insert(std::move(c));
        }
    }

    bool solve() {
        std::cout << "[CDCL/Resolution Engine] Старт насичення. Початкових диз'юнктів: "
                  << clause_db_.size() << std::endl;

        for (const auto& c : clause_db_) {
            if (c.empty()) {
                std::cout << "[Збій] Порожній диз'юнкт ⊥ присутній у вхідній формулі!\n";
                return true;
            }
        }

        bool new_clause_added = true;
        size_t iteration = 1;

        while (new_clause_added) {
            new_clause_added = false;
            std::vector<Clause> current_clauses(clause_db_.begin(), clause_db_.end());
            std::cout << "--- Ітерація " << iteration++ << " (поточний розмір: " 
                      << current_clauses.size() << ") ---\n";

            for (size_t i = 0; i < current_clauses.size(); ++i) {
                for (size_t j = i + 1; j < current_clauses.size(); ++j) {
                    for (int v = 1; v <= num_vars_; ++v) {
                        auto res = resolve(current_clauses[i], current_clauses[j], v);
                        if (res.has_value()) {
                            if (res->empty()) {
                                std::cout << "[УСПІХ] Резолюційний вивід досяг ⊥!\n"
                                          << "Резолюція між " << current_clauses[i].to_string()
                                          << " та " << current_clauses[j].to_string() 
                                          << " за змінною x" << v << "\n";
                                return true; // UNSAT
                            }
                            if (clause_db_.find(*res) == clause_db_.end()) {
                                clause_db_.insert(*res);
                                new_clause_added = true;
                            }
                        }
                    }
                }
            }
        }

        std::cout << "[РЕЗУЛЬТАТ] Формула здійсненна (SAT). Резолюція ⊥ неможлива.\n";
        return false;
    }
};

int main() {
    // Демонстрація на нездійсненному наборі з 3 variables
    ResolutionSolver solver(3);

    // F = (x1 ∨ x2) ∧ (¬x1 ∨ x3) ∧ (¬x2 ∨ x3) ∧ (¬x3)
    solver.add_clause(Clause({1, 2}));
    solver.add_clause(Clause({-1, 3}));
    solver.add_clause(Clause({-2, 3}));
    solver.add_clause(Clause({-3}));

    bool unsat = solver.solve();
    std::cout << "Результат спростування (UNSAT): " << (unsat ? "ТАК" : "НІ") << std::endl;

    return 0;
}
