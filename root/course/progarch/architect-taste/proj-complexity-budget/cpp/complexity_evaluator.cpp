// complexity_evaluator.cpp - Ідіоматична реалізація аналізатора архітектури на C++20
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <unordered_map>
#include <unordered_set>
#include <algorithm>
#include <expected>
#include <format>

namespace arch_metrics {

struct Module {
    std::string name;
    bool is_pass_through{false};
    std::vector<std::string> outgoing_calls;
};

enum class EvaluationError {
    EmptyGraph,
    CyclicDependencyDetected
};

class CallGraphAnalyzer {
public:
    void add_module(std::string name, bool is_pass_through, std::vector<std::string> calls = {}) {
        modules_[name] = Module{
            .name = std::move(name),
            .is_pass_through = is_pass_through,
            .outgoing_calls = std::move(calls)
        };
    }

    struct MetricsReport {
        std::size_t total_modules;
        std::size_t max_depth;
        double wrapper_ratio;
        bool passes_taste_gate;
    };

    [[nodiscard]] std::expected<MetricsReport, EvaluationError> analyze() const {
        if (modules_.empty()) {
            return std::unexpected(EvaluationError::EmptyGraph);
        }

        std::size_t max_depth = 0;
        std::size_t pass_through_count = 0;

        for (const auto& [name, mod] : modules_) {
            if (mod.is_pass_through) {
                pass_through_count++;
            }
            std::unordered_set<std::string_view> visited;
            auto depth = compute_depth(name, visited);
            if (!depth) {
                return std::unexpected(depth.error());
            }
            max_depth = std::max(max_depth, *depth);
        }

        double ratio = static_cast<double>(pass_through_count) / modules_.size();
        bool passes = (max_depth <= 5) && (ratio <= 0.30);

        return MetricsReport{
            .total_modules = modules_.size(),
            .max_depth = max_depth,
            .wrapper_ratio = ratio,
            .passes_taste_gate = passes
        };
    }

private:
    std::unordered_map<std::string, Module> modules_;

    std::expected<std::size_t, EvaluationError> compute_depth(
        std::string_view current,
        std::unordered_set<std::string_view>& visited) const
    {
        if (visited.contains(current)) {
            return std::unexpected(EvaluationError::CyclicDependencyDetected);
        }

        auto it = modules_.find(std::string(current));
        if (it == modules_.end() || it->second.outgoing_calls.empty()) {
            return 1;
        }

        visited.insert(current);
        std::size_t max_sub_depth = 0;

        for (const auto& target : it->second.outgoing_calls) {
            auto sub = compute_depth(target, visited);
            if (!sub) return sub;
            max_sub_depth = std::max(max_sub_depth, *sub);
        }

        visited.erase(current);
        return 1 + max_sub_depth;
    }
};

} // namespace arch_metrics

int main() {
    using namespace arch_metrics;

    CallGraphAnalyzer analyzer;
    analyzer.add_module("HTTPController", true, {"RequestValidatorAdapter"});
    analyzer.add_module("RequestValidatorAdapter", true, {"DeviceCommandService"});
    analyzer.add_module("DeviceCommandService", true, {"AccessControlMediator"});
    analyzer.add_module("AccessControlMediator", true, {"GenericRuleEngineFactory"});
    analyzer.add_module("GenericRuleEngineFactory", true, {"LockHardwareExecutor"});
    analyzer.add_module("LockHardwareExecutor", false, {});

    auto result = analyzer.analyze();
    if (result) {
        const auto& r = *result;
        std::cout << std::format("=== ARCHITECTURAL TASTE METRICS REPORT (C++20) ===\n"
                                 "Total Modules Registered : {}\n"
                                 "Max Indirection Depth    : {}\n"
                                 "Wrapper Module Ratio     : {:.2f}\n"
                                 "Passes Taste Gate        : {}\n",
                                 r.total_modules, r.max_depth, r.wrapper_ratio,
                                 r.passes_taste_gate ? "YES (Clean Elegance)" : "NO (Over-engineered)");
    } else {
        std::cerr << "Analysis failed due to graph errors.\n";
    }

    return 0;
}
