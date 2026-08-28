#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <algorithm>

enum class FactId : uint8_t {
    VoltageMv = 0,
    CurrentMa,
    TempC,
    PressureKpa,
    EstopPressed,
    Count
};

enum class ConditionOp : uint8_t {
    LessThan,
    GreaterThan,
    Equals,
    InRange,
    BitSet
};

struct Fact {
    int32_t value{0};
    uint32_t last_update_ms{0};
    bool is_valid{false};
};

using ActionCallback = void(*)(void* context, int32_t param);

struct RuleDef {
    uint8_t rule_id;
    FactId fact_id;
    ConditionOp op;
    int32_t threshold_low;
    int32_t threshold_high;
    uint32_t dwell_time_ms;
    uint32_t interlock_mask;
    uint32_t set_interlock;
    ActionCallback action{nullptr};
    int32_t action_param{0};
};

struct RuleState {
    uint32_t condition_true_since_ms{0};
    bool is_active{false};
    bool condition_was_true{false};
};

template <size_t MaxFacts = 16, size_t MaxRules = 8>
class DeterministicRuleEngine {
public:
    explicit constexpr DeterministicRuleEngine(std::span<const RuleDef> rules, void* context = nullptr) noexcept
        : rules_(rules), user_context_(context) {}

    void set_fact(FactId id, int32_t val, uint32_t now_ms) noexcept {
        const auto idx = static_cast<size_t>(id);
        if (idx < facts_.size()) {
            facts_[idx] = Fact{
                .value = val,
                .last_update_ms = now_ms,
                .is_valid = true
            };
        }
    }

    void invalidate_fact(FactId id) noexcept {
        const auto idx = static_cast<size_t>(id);
        if (idx < facts_.size()) {
            facts_[idx].is_valid = false;
        }
    }

    void step(uint32_t now_ms) noexcept {
        uint32_t next_interlocks = 0;
        const size_t count = std::min(rules_.size(), states_.size());

        for (size_t i = 0; i < count; ++i) {
            const auto& rule = rules_[i];
            auto& state = states_[i];
            const auto fact_idx = static_cast<size_t>(rule.fact_id);
            const auto& fact = facts_[fact_idx];

            if ((active_interlocks_ & rule.interlock_mask) != 0) {
                state.condition_was_true = false;
                state.is_active = false;
                continue;
            }

            if (evaluate_condition(rule, fact)) {
                if (!state.condition_was_true) {
                    state.condition_was_true = true;
                    state.condition_true_since_ms = now_ms;
                }

                if ((now_ms - state.condition_true_since_ms) >= rule.dwell_time_ms) {
                    if (!state.is_active) {
                        state.is_active = true;
                        if (rule.action != nullptr) {
                            rule.action(user_context_, rule.action_param);
                        }
                    }
                    next_interlocks |= rule.set_interlock;
                }
            } else {
                state.condition_was_true = false;
                state.is_active = false;
            }
        }

        active_interlocks_ = next_interlocks;
    }

    [[nodiscard]] constexpr uint32_t active_interlocks() const noexcept {
        return active_interlocks_;
    }

private:
    [[nodiscard]] static constexpr bool evaluate_condition(const RuleDef& rule, const Fact& fact) noexcept {
        if (!fact.is_valid) {
            return false;
        }
        switch (rule.op) {
            case ConditionOp::LessThan:
                return fact.value < rule.threshold_low;
            case ConditionOp::GreaterThan:
                return fact.value > rule.threshold_high;
            case ConditionOp::Equals:
                return fact.value == rule.threshold_low;
            case ConditionOp::InRange:
                return (fact.value >= rule.threshold_low) && 
                       (fact.value <= rule.threshold_high);
            case ConditionOp::BitSet:
                return (fact.value & rule.threshold_low) != 0;
            default:
                return false;
        }
    }

    std::span<const RuleDef> rules_;
    void* user_context_{nullptr};
    std::array<Fact, MaxFacts> facts_{};
    std::array<RuleState, MaxRules> states_{};
    uint32_t active_interlocks_{0};
};
