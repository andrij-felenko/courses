/**
 * @file FailsafeDispatcher.hpp
 * @brief C++20 диспетчер пріоритетів аварійних станів автопілота.
 */

#include <cstdint>
#include <array>
#include <span>

namespace autopilot::safety {

enum class Cap : uint8_t {
    AttitudeOk   = 1u << 0,
    AltitudeOk   = 1u << 1,
    PositionOk   = 1u << 2,
    PropulsionOk = 1u << 3
};

constexpr uint8_t operator|(Cap lhs, Cap rhs) noexcept {
    return static_cast<uint8_t>(lhs) | static_cast<uint8_t>(rhs);
}

enum class Action : uint8_t {
    None = 0,
    Warn,
    AltHold,
    ReturnToLaunch,
    EmergencyLand,
    TerminateFlight
};

struct FailureRule {
    uint8_t rank{255};
    uint8_t required_caps{0};
    Action  desired_action{Action::None};
    Action  fallback_action{Action::None};
    bool    latch{false};
};

class FailsafeDispatcher {
public:
    static constexpr size_t RuleCount = 5;

    constexpr FailsafeDispatcher() = default;

    Action evaluate(uint8_t raw_failures_mask, uint8_t available_caps) noexcept {
        uint8_t best_rank = 255;
        Action best_action = Action::None;

        for (size_t i = 0; i < RuleCount; ++i) {
            const auto& rule = rules_[i];
            const bool active = (raw_failures_mask & (1u << i)) != 0;

            if (active || latched_states_[i]) {
                if (rule.latch) {
                    latched_states_[i] = true;
                }

                if (rule.rank < best_rank) {
                    const bool caps_ok = (available_caps & rule.required_caps) == rule.required_caps;
                    const Action effective = caps_ok ? rule.desired_action : rule.fallback_action;

                    best_rank = rule.rank;
                    best_action = effective;
                }
            }
        }

        current_action_ = best_action;
        current_rank_ = best_rank;
        return current_action_;
    }

    [[nodiscard]] Action current_action() const noexcept { return current_action_; }
    [[nodiscard]] uint8_t current_rank() const noexcept { return current_rank_; }

private:
    static constexpr std::array<FailureRule, RuleCount> rules_{{
        { .rank = 0, .required_caps = 0, .desired_action = Action::TerminateFlight, .fallback_action = Action::TerminateFlight, .latch = true },
        { .rank = 1, .required_caps = static_cast<uint8_t>(Cap::AttitudeOk), .desired_action = Action::EmergencyLand, .fallback_action = Action::TerminateFlight, .latch = true },
        { .rank = 2, .required_caps = Cap::PositionOk | Cap::AltitudeOk, .desired_action = Action::ReturnToLaunch, .fallback_action = Action::EmergencyLand, .latch = false },
        { .rank = 3, .required_caps = Cap::PositionOk | Cap::AltitudeOk, .desired_action = Action::ReturnToLaunch, .fallback_action = Action::EmergencyLand, .latch = false },
        { .rank = 4, .required_caps = static_cast<uint8_t>(Cap::AltitudeOk), .desired_action = Action::AltHold, .fallback_action = Action::EmergencyLand, .latch = false }
    }};

    std::array<bool, RuleCount> latched_states_{};
    Action current_action_{Action::None};
    uint8_t current_rank_{255};
};

} // namespace autopilot::safety
