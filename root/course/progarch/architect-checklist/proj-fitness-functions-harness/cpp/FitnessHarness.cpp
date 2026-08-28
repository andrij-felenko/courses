// FitnessHarness.cpp — Архітектурний контролер для C++20 / Backend
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <expected>
#include <memory>
#include <unordered_set>
#include <regex>

struct ServiceNode {
    std::string name;
    std::string layer; // "Domain", "Application", "Infrastructure"
    std::unordered_set<std::string> dependencies;
    bool has_circuit_breaker{false};
    double network_timeout_ms{0.0};
    bool has_w3c_tracing{false};
};

enum class ViolationSeverity { Warning, CriticalBlocker };

struct ArchitectureViolation {
    std::string rule_id;
    std::string message;
    ViolationSeverity severity;
};

class FitnessHarnessEvaluator {
public:
    explicit FitnessHarnessEvaluator(std::vector<ServiceNode> nodes)
        : nodes_(std::move(nodes)) {}

    [[nodiscard]] std::expected<void, std::vector<ArchitectureViolation>> evaluate_gate() const {
        std::vector<ArchitectureViolation> violations;

        for (const auto& node : nodes_) {
            // Крок 1. Перевірка інваріанта ізоляції доменного шару (Clean Architecture Gate)
            if (node.layer == "Domain") {
                for (const auto& dep : node.dependencies) {
                    if (dep.find("Infrastructure") != std::string::npos ||
                        dep.find("HttpAdapter") != std::string::npos) {
                        violations.push_back({
                            "RULE-01-DOMAIN-ISOLATION",
                            "Доменний модуль '" + node.name + "' імпортує інфраструктурний модуль '" + dep + "'",
                            ViolationSeverity::CriticalBlocker
                        });
                    }
                }
            }

            // Крок 2. Перевірка наявності Circuit Breaker та таймаутів при мережевих викликах
            if (!node.dependencies.empty()) {
                if (node.network_timeout_ms <= 0.0 || node.network_timeout_ms > 1000.0) {
                    violations.push_back({
                        "RULE-02-NETWORK-TIMEOUT-BUDGET",
                        "Сервіс '" + node.name + "' має небезпечний мережевий таймаут: " + 
                            std::to_string(node.network_timeout_ms) + " мс (дозволено: 1..1000 мс)",
                        ViolationSeverity::CriticalBlocker
                    });
                }
                if (!node.has_circuit_breaker) {
                    violations.push_back({
                        "RULE-03-CIRCUIT-BREAKER-MISSING",
                        "Зовнішні виклики в '" + node.name + "' не захищені Circuit Breaker",
                        ViolationSeverity::CriticalBlocker
                    });
                }
            }

            // Крок 3. Валідація спостережуваності (W3C Tracing)
            if (!node.has_w3c_tracing) {
                violations.push_back({
                    "RULE-04-OBSERVABILITY-TRACING",
                    "Відсутня простежуваність (W3C Trace Context) у сервісі '" + node.name + "'",
                    ViolationSeverity::Warning
                });
            }
        }

        if (has_critical_blockers(violations)) {
            return std::unexpected(violations);
        }
        return {};
    }

private:
    std::vector<ServiceNode> nodes_;

    static bool has_critical_blockers(const std::vector<ArchitectureViolation>& list) {
        for (const auto& v : list) {
            if (v.severity == ViolationSeverity::CriticalBlocker) {
                return true;
            }
        }
        return false;
    }
};

int main() {
    std::vector<ServiceNode> architecture_graph = {
        {"EnergyCoreDomain", "Domain", {"SharedUtils"}, true, 0.0, true},
        {"SmartLockAdapter", "Infrastructure", {"EnergyCoreDomain", "RedisDriver"}, true, 250.0, true},
        {"UnsafeGateway", "Application", {"InfrastructureHttpAdapter"}, false, 5000.0, false}
    };

    FitnessHarnessEvaluator evaluator(architecture_graph);
    auto result = evaluator.evaluate_gate();

    if (!result) {
        std::cerr << "[FITNESS HARNESS] ✖ АРХІТЕКТУРНИЙ ГЕЙТ НЕ ПРОЙДЕНО!\n";
        for (const auto& violation : result.error()) {
            std::cerr << "  - [" << violation.rule_id << "] " 
                      << (violation.severity == ViolationSeverity::CriticalBlocker ? "CRITICAL: " : "WARN: ")
                      << violation.message << "\n";
        }
        return 1;
    }

    std::cout << "[FITNESS HARNESS] ✔ Усі архітектурні інваріанти задоволено.\n";
    return 0;
}
