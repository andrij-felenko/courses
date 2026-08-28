#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <variant>
#include <memory>
#include <atomic>
#include <cstdint>
#include <algorithm>
#include <cstring>

// Атрибути користувача: підтримуємо рядки, числа та булеві значення
using AttributeValue = std::variant<std::string, double, bool>;

struct EvaluationContext {
    std::string targeting_key;
    std::unordered_map<std::string, AttributeValue> attributes;
};

// Реалізація алгоритму MurmurHash3_x86_32 для детермінованого бакетування
uint32_t murmur3_32(std::string_view key, uint32_t seed = 0) {
    uint32_t h = seed;
    const size_t nblocks = key.size() / 4;
    const uint32_t* blocks = reinterpret_cast<const uint32_t*>(key.data());

    for (size_t i = 0; i < nblocks; ++i) {
        uint32_t k = blocks[i];
        k *= 0xcc9e2d51;
        k = (k << 15) | (k >> 17);
        k *= 0x1b873593;

        h ^= k;
        h = (h << 13) | (h >> 19);
        h = h * 5 + 0xe6546b64;
    }

    const uint8_t* tail = reinterpret_cast<const uint8_t*>(key.data() + nblocks * 4);
    uint32_t k1 = 0;
    switch (key.size() & 3) {
        case 3: k1 ^= static_cast<uint32_t>(tail[2]) << 16; [[fallthrough]];
        case 2: k1 ^= static_cast<uint32_t>(tail[1]) << 8;  [[fallthrough]];
        case 1: k1 ^= static_cast<uint32_t>(tail[0]);
                k1 *= 0xcc9e2d51;
                k1 = (k1 << 15) | (k1 >> 17);
                k1 *= 0x1b873593;
                h ^= k1;
    }

    h ^= static_cast<uint32_t>(key.size());
    h ^= h >> 16;
    h *= 0x85ebca6b;
    h ^= h >> 13;
    h *= 0xc2b2ae35;
    h ^= h >> 16;
    return h;
}

// Правило таргетингу за атрибутом (наприклад, country == "UA")
struct TargetingRule {
    std::string attribute_name;
    std::string expected_string_value;
    bool enabled_value;
};

// Конфігурація окремого прапорця
struct FlagDefinition {
    std::string key;
    bool default_value = false;
    uint32_t rollout_percentage = 0; // 0 - 100%
    std::vector<std::string> whitelist_users;
    std::vector<TargetingRule> rules;
};

// Незмінний набір усіх правил системи
struct RuleSet {
    std::unordered_map<std::string, FlagDefinition> flags;
};

// Результат обчислення прапорця
struct EvaluationResult {
    bool value;
    std::string_view reason; // "OVERRIDE", "RULE_MATCH", "PERCENTAGE_ROLLOUT", "DEFAULT"
};

// Двигунець обчислення в пам'яті з атомарним оновленням
class FlagEngine {
public:
    FlagEngine() : ruleset_(std::make_shared<RuleSet>()) {}

    // Неблокуюче обчислення значення (гарячий шлях)
    EvaluationResult evaluate(std::string_view flag_key, const EvaluationContext& ctx) const {
        // Атомарно захоплюємо поточний знімок конфігурації (acquire semantics)
        auto current_rules = std::atomic_load_explicit(&ruleset_, std::memory_order_acquire);
        
        auto it = current_rules->flags.find(std::string(flag_key));
        if (it == current_rules->flags.end()) {
            return { false, "FLAG_NOT_FOUND" };
        }

        const auto& flag = it->second;

        // 1. Перевірка списку індивідуальних перевизначень (Whitelist)
        for (const auto& user_id : flag.whitelist_users) {
            if (user_id == ctx.targeting_key) {
                return { true, "OVERRIDE" };
            }
        }

        // 2. Перевірка правил таргетингу за контекстними атрибутами
        for (const auto& rule : flag.rules) {
            auto attr_it = ctx.attributes.find(rule.attribute_name);
            if (attr_it != ctx.attributes.end()) {
                if (const auto* str_val = std::get_if<std::string>(&attr_it->second)) {
                    if (*str_val == rule.expected_string_value) {
                        return { rule.enabled_value, "RULE_MATCH" };
                    }
                }
            }
        }

        // 3. Перевірка відсоткової розкатки за MurmurHash3
        if (flag.rollout_percentage > 0 && !ctx.targeting_key.empty()) {
            // Формуємо ключ: flag_key + ":" + targeting_key
            std::string hash_input = std::string(flag_key) + ":" + ctx.targeting_key;
            uint32_t hash_val = murmur3_32(hash_input);
            uint32_t bucket = hash_val % 100;

            if (bucket < flag.rollout_percentage) {
                return { true, "PERCENTAGE_ROLLOUT" };
            }
        }

        // 4. Повернення значення за замовчуванням
        return { flag.default_value, "DEFAULT" };
    }

    // Фонове атомарне оновлення конфігурації правил
    void update_rules(std::shared_ptr<RuleSet> new_rules) {
        std::atomic_store_explicit(&ruleset_, std::move(new_rules), std::memory_order_release);
    }

private:
    alignas(64) std::shared_ptr<RuleSet> ruleset_;
};
