#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <filesystem>
#include <regex>
#include <expected>

namespace fs = std::filesystem;

struct ContextRule {
    std::string source_context;
    std::unordered_set<std::string> allowed_imports;
};

class ConwayBoundaryChecker {
public:
    explicit ConwayBoundaryChecker(std::vector<ContextRule> rules) {
        for (auto& r : rules) {
            rules_map_[std::move(r.source_context)] = std::move(r.allowed_imports);
        }
    }

    [[nodiscard]] std::expected<std::vector<std::string>, std::string> 
    check_file(const fs::path& file_path, std::string_view current_context) const {
        std::ifstream file(file_path);
        if (!file.is_open()) {
            return std::unexpected("Не вдалося відкрити файл: " + file_path.string());
        }

        std::vector<std::string> violations;
        auto it = rules_map_.find(std::string(current_context));
        const static std::unordered_set<std::string> empty_set;
        const auto& allowed = (it != rules_map_.end()) ? it->second : empty_set;

        std::string line;
        const std::regex include_regex(R"(^\s*#include\s+["<]([^"/>]+)/.*[">])");
        std::smatch match;

        while (std::getline(file, line)) {
            if (std::regex_search(line, match, include_regex)) {
                std::string imported_context = match[1].str();
                
                if (imported_context == current_context || imported_context == "iostream" || imported_context == "vector") {
                    continue;
                }

                if (!allowed.contains(imported_context)) {
                    violations.push_back(
                        "Порушення межі Конвея у " + file_path.string() + 
                        ": контекст '" + std::string(current_context) + "' включає заголовок з '" + 
                        imported_context + "', що не є в списку дозволених."
                    );
                }
            }
        }
        return violations;
    }

private:
    std::unordered_map<std::string, std::unordered_set<std::string>> rules_map_;
};

int main() {
    std::vector<ContextRule> rules = {
        {"automations", {"twin_contracts", "identity_sdk", "event_bus"}},
        {"device_control", {"hub_acl_contracts", "identity_sdk"}},
    };

    ConwayBoundaryChecker checker(rules);
    auto result = checker.check_file("automations/engine.cpp", "automations");

    if (!result) {
        std::cerr << "Помилка аналізу: " << result.error() << '\n';
        return 1;
    }

    if (!result->empty()) {
        std::cout << "❌ ВИЯВЛЕНО ПОРУШЕННЯ МЕЖ КОНТЕКСТІВ:\n";
        for (const auto& v : *result) {
            std::cout << "  · " << v << '\n';
        }
        return 1;
    }

    std::cout << "✅ Межі контекстів C++ код бази чисті!\n";
    return 0;
}
