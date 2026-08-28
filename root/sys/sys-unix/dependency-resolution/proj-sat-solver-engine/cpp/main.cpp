#include <iostream>
#include <vector>
#include <optional>
#include <numeric>
#include <string_view>
#include <cmath>

enum class PackageState : int8_t {
    Unassigned = 0,
    Installed = 1,
    Absent = -1
};

struct SatClause {
    std::vector<int> literals; // Позитивний значення (+ID), негативне (-ID)
};

class PackageDependencySolver {
public:
    explicit PackageDependencySolver(size_t package_count)
        : assignments_(package_count + 1, PackageState::Unassigned) {}

    void add_clause(std::vector<int> lits) {
        clauses_.push_back(SatClause{std::move(lits)});
    }

    // Створення правила залежності: pkg_a => pkg_b (-A v B)
    void add_dependency(int pkg_a, int pkg_b) {
        add_clause({-pkg_a, pkg_b});
    }

    // Створення правила конфлікту: NOT (pkg_a AND pkg_b) (-A v -B)
    void add_conflict(int pkg_a, int pkg_b) {
        add_clause({-pkg_a, -pkg_b});
    }

    // Створення прямого запиту користувача (+pkg_id)
    void require_package(int pkg_id) {
        add_clause({pkg_id});
    }

    // Запуск розв'язання залежностей
    [[nodiscard]] std::optional<std::vector<PackageState>> solve() {
        if (!unit_propagate()) {
            return std::nullopt; // Нездійсненна система
        }

        int unassigned_var = find_unassigned_variable();
        if (unassigned_var == 0) {
            return assignments_; // Усі змінні успішно призначені
        }

        // Збереження стану для відкату (RAII)
        auto saved_state = assignments_;

        // Гілка 1: Спробуємо призначити Installed
        assignments_[unassigned_var] = PackageState::Installed;
        if (auto result = solve()) {
            return result;
        }

        // Гілка 2: Відкат та спроба призначити Absent
        assignments_ = std::move(saved_state);
        assignments_[unassigned_var] = PackageState::Absent;
        return solve();
    }

private:
    std::vector<SatClause> clauses_;
    std::vector<PackageState> assignments_;

    int find_unassigned_variable() const {
        for (size_t i = 1; i < assignments_.size(); ++i) {
            if (assignments_[i] == PackageState::Unassigned) {
                return static_cast<int>(i);
            }
        }
        return 0;
    }

    bool unit_propagate() {
        bool changed = true;
        while (changed) {
            changed = false;
            for (const auto& clause : clauses_) {
                int unassigned_lit = 0;
                int unassigned_count = 0;
                bool satisfied = false;

                for (int lit : clause.literals) {
                    int var = std::abs(lit);
                    auto val = assignments_[var];

                    if ((lit > 0 && val == PackageState::Installed) || 
                        (lit < 0 && val == PackageState::Absent)) {
                        satisfied = true;
                        break;
                    }
                    if (val == PackageState::Unassigned) {
                        unassigned_count++;
                        unassigned_lit = lit;
                    }
                }

                if (satisfied) continue;
                if (unassigned_count == 0) return false; // Конфлікт!

                if (unassigned_count == 1 && unassigned_lit != 0) {
                    int var = std::abs(unassigned_lit);
                    assignments_[var] = (unassigned_lit > 0) ? PackageState::Installed : PackageState::Absent;
                    changed = true;
                }
            }
        }
        return true;
    }
};

int main() {
    // Ініціалізація системи на 4 пакунки
    PackageDependencySolver solver(4);

    // Додавання правил графа
    solver.add_dependency(1, 2); // App (1) -> LibA (2)
    solver.add_dependency(1, 3); // App (1) -> Postfix (3)
    solver.add_conflict(3, 4);   // Postfix (3) <-> Sendmail (4)

    // Запит користувача: встановити App (1)
    solver.require_package(1);

    std::cout << "Аналіз графа залежностей C++20 SAT-солвером...\n";
    auto result = solver.solve();

    if (result) {
        std::cout << "ПЛАН ТРАНЗАЦІЇ УСПІШНО СФОРМОВАНО:\n";
        constexpr std::string_view names[] = {"", "App", "LibA", "Postfix", "Sendmail"};
        for (size_t i = 1; i <= 4; ++i) {
            std::cout << "  - " << names[i] << " (ID " << i << "): "
                      << ((*result)[i] == PackageState::Installed ? "УСТАНОВИТИ" : "ПРОПУСТИТИ")
                      << "\n";
        }
    } else {
        std::cout << "ТРАНЗАЦІЯ БЛОКОВАНА: Виявлено незадоволений конфлікт версій!\n";
    }

    return 0;
}
