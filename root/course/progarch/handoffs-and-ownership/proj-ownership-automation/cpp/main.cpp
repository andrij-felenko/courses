// cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <algorithm>

enum class OwnershipMode {
    Strong,
    InnerSource
};

enum class Verdict {
    Allow,
    NeedReview,
    Reject
};

struct OwnershipRule {
    std::string path_prefix;
    std::string owner_team;
    OwnershipMode mode;
};

class OwnershipEngine {
public:
    void add_rule(std::string_view prefix, std::string_view owner, OwnershipMode mode) {
        rules_.push_back({std::string(prefix), std::string(owner), mode});
    }

    [[nodiscard]] Verdict evaluate_change(std::string_view file_path,
                                         std::string_view author_team,
                                         bool is_contract_broken) const noexcept {
        const OwnershipRule* best_rule = nullptr;
        size_t max_match_len = 0;

        for (const auto& rule : rules_) {
            if (file_path.starts_with(rule.path_prefix) && rule.path_prefix.length() > max_match_len) {
                max_match_len = rule.path_prefix.length();
                best_rule = &rule;
            }
        }

        if (!best_rule) {
            return Verdict::Allow;
        }

        if (author_team == best_rule->owner_team) {
            return Verdict::Allow;
        }

        if (best_rule->mode == OwnershipMode::Strong) {
            return Verdict::NeedReview;
        }

        if (is_contract_broken) {
            return Verdict::Reject;
        }

        return Verdict::NeedReview;
    }

private:
    std::vector<OwnershipRule> rules_;
};

int main() {
    OwnershipEngine engine;
    engine.add_rule("src/core/crypto/", "sec-team", OwnershipMode::Strong);
    engine.add_rule("src/services/telemetry/", "platform-team", OwnershipMode::InnerSource);

    std::cout << "Test 1 (Owner PR): " 
              << static_cast<int>(engine.evaluate_change("src/core/crypto/sha256.cpp", "sec-team", false)) << "\n";
    std::cout << "Test 2 (External PR Strong): " 
              << static_cast<int>(engine.evaluate_change("src/core/crypto/sha256.cpp", "billing-team", false)) << "\n";
    std::cout << "Test 3 (InnerSource PR Contract OK): " 
              << static_cast<int>(engine.evaluate_change("src/services/telemetry/ingest.cpp", "billing-team", false)) << "\n";
    std::cout << "Test 4 (InnerSource PR Contract Broken): " 
              << static_cast<int>(engine.evaluate_change("src/services/telemetry/ingest.cpp", "billing-team", true)) << "\n";

    return 0;
}
