// fitness_checker.cpp — Статичний перевірник меж контекстів та зчеплення команд у C++20
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <span>
#include <stdexcept>
#include <algorithm>

struct DependencyEdge {
    std::string source_team;
    std::string source_context;
    std::string target_context;
    std::string imported_symbol;
    bool is_public_contract;
};

class ArchitectureFitnessChecker {
public:
    explicit ArchitectureFitnessChecker(size_t max_efferent_coupling = 2)
        : max_efferent_coupling_(max_efferent_coupling) {}

    void add_dependency(const DependencyEdge& edge) {
        dependencies_.push_back(edge);
    }

    struct Violation {
        std::string team;
        std::string description;
        std::string severity; // "CRITICAL" or "WARNING"
    };

    std::vector<Violation> evaluate_rules() const {
        std::vector<Violation> violations;

        // Перевірка 1: Прямі імпорти приватних нутрощів чужого контексту
        for (const auto& dep : dependencies_) {
            if (!dep.is_public_contract && dep.source_context != dep.target_context) {
                violations.push_back({
                    dep.source_team,
                    "Порушення межі контексту: Команда '" + dep.source_team + 
                    "' в контексті '" + dep.source_context + 
                    "' імпортує приватний символ '" + dep.imported_symbol + 
                    "' з чужого контексту '" + dep.target_context + "'. Використовуйте публічний API-контракт!",
                    "CRITICAL"
                });
            }
        }

        // Перевірка 2: Еферентне зчеплення (Efferent Coupling Ce)
        std::unordered_map<std::string, std::unordered_set<std::string>> outgoing_deps;
        for (const auto& dep : dependencies_) {
            if (dep.source_context != dep.target_context) {
                outgoing_deps[dep.source_context].insert(dep.target_context);
            }
        }

        for (const auto& [ctx, targets] : outgoing_deps) {
            if (targets.size() > max_efferent_coupling_) {
                violations.push_back({
                    ctx + "_owner",
                    "Перевищення когнітивного навантаження: Контекст '" + ctx + 
                    "' залежить від " + std::to_string(targets.size()) + 
                    " інших контекстів (ліміт: " + std::to_string(max_efferent_coupling_) + 
                    "). Необхідно провести декомпозицію!",
                    "WARNING"
                });
            }
        }

        return violations;
    }

private:
    size_t max_efferent_coupling_;
    std::vector<DependencyEdge> dependencies_;
};

int main() {
    try {
        ArchitectureFitnessChecker checker(2);

        // Граф залежностей проєкту Digital Homes
        checker.add_dependency({"PaymentsTeam", "BillingContext", "DeviceContext", "dh::devices::DeviceContractDTO", true});
        checker.add_dependency({"PaymentsTeam", "BillingContext", "TelemetryContext", "dh::telemetry::internal::RawDatabasePool", false}); // VIOLATION!
        checker.add_dependency({"PaymentsTeam", "BillingContext", "AuthContext", "dh::auth::UserToken", true});
        checker.add_dependency({"PaymentsTeam", "BillingContext", "NotificationContext", "dh::notify::SendAlert", true}); // Coupling > 2!

        auto violations = checker.evaluate_rules();

        std::cout << "=== Результати запуску Architecture Fitness Gate ===" << std::endl;
        bool has_critical = false;
        for (const auto& v : violations) {
            std::cout << "[" << v.severity << "] Команда/Контекст: " << v.team 
                      << "\n    " << v.description << std::endl;
            if (v.severity == "CRITICAL") has_critical = true;
        }

        if (has_critical) {
            std::cerr << "\nCI/CD GATE FAILED: Виявлено критичні порушення соціотехнічних меж!" << std::endl;
            return 1;
        }

        std::cout << "\nCI/CD GATE PASSED: Соціотехнічні межі дотримано." << std::endl;
        return 0;
    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання: " << ex.what() << std::endl;
        return 2;
    }
}
