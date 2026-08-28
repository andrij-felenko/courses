/**
 * @file FailsafePrioritizer.hpp
 * @brief Високонадійний C++20 модуль арбітражу аварійних ситуацій.
 */

#pragma once

#include <cstdint>
#include <array>
#include <string_view>
#include <algorithm>
#include <optional>

namespace autopilot::safety {

enum class Capability : uint16_t {
    AttitudeEstimate  = 1u << 0,
    AltitudeEstimate  = 1u << 1,
    Position3DFix     = 1u << 2,
    PropulsionControl = 1u << 3,
    CommunicationLink = 1u << 4
};

constexpr uint16_t operator|(Capability lhs, Capability rhs) noexcept {
    return static_cast<uint16_t>(lhs) | static_cast<uint16_t>(rhs);
}

enum class Action : uint8_t {
    None = 0,
    WarnOnly,
    AltHoldDrift,
    HoldPosition,
    ReturnToLaunch,
    EmergencyLand,
    DeployParachute,
    TerminateFlight
};

struct Rule {
    uint8_t          priority{255};
    uint16_t         required_caps{0};
    Action           desired_action{Action::None};
    Action           fallback_action{Action::None};
    uint16_t         confirm_delay_ms{0};
    bool             is_latched{false};
    std::string_view name{"Unknown"};
};

template <size_t MaxRules = 16>
class FailsafePrioritizer {
public:
    constexpr FailsafePrioritizer() = default;

    bool add_rule(const Rule& rule) noexcept {
        if (rule_count_ >= MaxRules) return false;
        rules_[rule_count_] = rule;
        timers_ms_[rule_count_] = 0;
        latched_states_[rule_count_] = false;
        ++rule_count_;
        return true;
    }

    Action update(
        uint16_t raw_failures_mask,
        uint16_t available_caps,
        uint16_t delta_time_ms
    ) noexcept {
        uint8_t best_priority = 255;
        Action best_action = Action::None;
        int best_rule_idx = -1;

        for (size_t i = 0; i < rule_count_; ++i) {
            const auto& r = rules_[i];
            const bool is_active = (raw_failures_mask & (1u << i)) != 0;

            // Фаза 1: Дебаунсинг інтегратором
            if (is_active) {
                timers_ms_[i] = std::min<uint16_t>(timers_ms_[i] + delta_time_ms, r.confirm_delay_ms);
            } else if (!latched_states_[i]) {
                timers_ms_[i] = (timers_ms_[i] > delta_time_ms) ? (timers_ms_[i] - delta_time_ms) : 0;
            }

            // Фаза 2: Кваліфікація
            const bool qualified = (timers_ms_[i] >= r.confirm_delay_ms) || latched_states_[i];
            if (qualified) {
                if (r.is_latched) {
                    latched_states_[i] = true;
                }

                // Фаза 3: Вибір за рангом та перевірка сенсорів
                if (r.priority < best_priority) {
                    const bool caps_ok = (available_caps & r.required_caps) == r.required_caps;
                    const Action effective = caps_ok ? r.desired_action : r.fallback_action;

                    best_priority = r.priority;
                    best_action = effective;
                    best_rule_idx = static_cast<int>(i);
                }
            }
        }

        // Фаза 4: Атомарне витіснення
        current_action_ = best_action;
        current_priority_ = best_priority;
        active_rule_index_ = best_rule_idx;

        return current_action_;
    }

    void reset_latches() noexcept {
        for (size_t i = 0; i < rule_count_; ++i) {
            latched_states_[i] = false;
            timers_ms_[i] = 0;
        }
        current_action_ = Action::None;
        current_priority_ = 255;
        active_rule_index_ = -1;
    }

    [[nodiscard]] Action current_action() const noexcept { return current_action_; }
    [[nodiscard]] uint8_t current_priority() const noexcept { return current_priority_; }
    [[nodiscard]] std::optional<std::string_view> active_rule_name() const noexcept {
        if (active_rule_index_ >= 0 && static_cast<size_t>(active_rule_index_) < rule_count_) {
            return rules_[active_rule_index_].name;
        }
        return std::nullopt;
    }

private:
    std::array<Rule, MaxRules>     rules_{};
    std::array<uint16_t, MaxRules> timers_ms_{};
    std::array<bool, MaxRules>     latched_states_{};
    size_t                         rule_count_{0};

    Action                         current_action_{Action::None};
    uint8_t                        current_priority_{255};
    int                            active_rule_index_{-1};
};

} // namespace autopilot::safety
