#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>
#include <cstdint>
#include <memory>
#include <atomic>

// 64-bit FNV-1a хеш-функція для рівномірного розподілу бакетів
uint64_t fnv1a_hash(const std::string& input) {
    uint64_t hash = 14695981039346656037ULL;
    for (char c : input) {
        hash ^= static_cast<uint64_t>(c);
        hash *= 1099511628211ULL;
    }
    return hash;
}

struct EvaluationContext {
    std::string user_id;
    std::string tenant_id;
    std::string user_role;
    std::unordered_map<std::string, std::string> attributes;
};

enum class FlagState {
    OFF,
    ON,
    PERCENTAGE_ROLLOUT,
    TARGETED
};

struct FeatureFlagRule {
    std::string flag_key;
    FlagState state = FlagState::OFF;
    uint32_t rollout_percentage = 0; // 0..100
    std::vector<std::string> allowed_roles;
    std::vector<std::string> allowed_user_ids;
};

class FeatureFlagEngine {
private:
    std::unordered_map<std::string, FeatureFlagRule> rules_;

public:
    void register_rule(const FeatureFlagRule& rule) {
        rules_[rule.flag_key] = rule;
    }

    bool is_enabled(const std::string& flag_key, const EvaluationContext& ctx) const {
        auto it = rules_.find(flag_key);
        if (it == rules_.end()) {
            return false; // За замовчуванням вимкнено (Safe Fallback)
        }

        const auto& rule = it->second;

        // 1. Абсолютні операційні рубильники (Emergency Kill-Switches)
        if (rule.state == FlagState::OFF) return false;
        if (rule.state == FlagState::ON) return true;

        // 2. Таргетовані користувачі (Explicit Allowlist / Beta Testers)
        for (const auto& uid : rule.allowed_user_ids) {
            if (uid == ctx.user_id) return true;
        }

        // 3. Перевірка обмеження ролей
        if (!rule.allowed_roles.empty()) {
            bool role_matched = false;
            for (const auto& role : rule.allowed_roles) {
                if (role == ctx.user_role) {
                    role_matched = true;
                    break;
                }
            }
            if (!role_matched) return false;
        }

        // 4. Детермінований відсотковий розкочувальний аналіз (Canary Rollout)
        if (rule.state == FlagState::PERCENTAGE_ROLLOUT) {
            if (rule.rollout_percentage == 0) return false;
            if (rule.rollout_percentage >= 100) return true;

            // Сіль (flag_key) захищає від кореляції між різними прапорцями
            std::string hash_input = flag_key + ":" + ctx.user_id;
            uint64_t hash_val = fnv1a_hash(hash_input);
            uint32_t bucket = static_cast<uint32_t>(hash_val % 100);

            return bucket < rule.rollout_percentage;
        }

        return false;
    }
};

int main() {
    FeatureFlagEngine engine;

    // Створюємо канарейкове правило для нового алгоритму розблокування смарт-замка DH
    FeatureFlagRule lock_v2_flag{
        "smart_lock_v2_algorithm",
        FlagState::PERCENTAGE_ROLLOUT,
        10, // 10% канарейка
        {}, // без обмеження за ролями
        {"beta_tester_99"} // конкретний бета-тестер завжди включений
    };

    engine.register_rule(lock_v2_flag);

    EvaluationContext user_beta{"beta_tester_99", "home_42", "resident", {}};
    EvaluationContext user_regular_1{"user_101", "home_12", "resident", {}};
    EvaluationContext user_regular_2{"user_204", "home_88", "resident", {}};

    std::cout << "Beta user test: " << engine.is_enabled("smart_lock_v2_algorithm", user_beta) << " (Expected: 1)\n";
    std::cout << "User 101 canary test: " << engine.is_enabled("smart_lock_v2_algorithm", user_regular_1) << "\n";
    std::cout << "User 204 canary test: " << engine.is_enabled("smart_lock_v2_algorithm", user_regular_2) << "\n";

    // Перевірка детермінованості повторного виклику
    bool first_eval = engine.is_enabled("smart_lock_v2_algorithm", user_regular_1);
    bool second_eval = engine.is_enabled("smart_lock_v2_algorithm", user_regular_1);
    std::cout << "Consistency check for user_101: " << (first_eval == second_eval ? "PASSED" : "FAILED") << "\n";

    return 0;
}
