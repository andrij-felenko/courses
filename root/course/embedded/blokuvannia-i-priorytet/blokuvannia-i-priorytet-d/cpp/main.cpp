#include <cstdint>
#include <cstddef>
#include <algorithm>
#include <array>
#include <optional>
#include <span>

namespace embedded::control {

enum class PriorityLevel : uint8_t {
    Automation = 0,
    Manual     = 1,
    Protection = 2,
    Safety     = 3
};

enum class DiscreteCommand : uint8_t {
    Stop    = 0,
    Forward = 1,
    Reverse = 2
};

enum class ArbitrationReason : uint8_t {
    None             = 0,
    NormalAuto       = 1,
    ManualOverride   = 2,
    ProtectionTrip   = 3,
    SafetyShutdown   = 4,
    DeadtimeHold     = 5
};

struct ActuatorRequest {
    uint8_t source_id{0};
    PriorityLevel priority{PriorityLevel::Automation};
    DiscreteCommand discrete_cmd{DiscreteCommand::Stop};
    float analog_setpoint{0.0f}; // 0.0f .. 1.0f
    uint32_t timestamp_ms{0};
    uint32_t ttl_ms{0};
    bool is_active{false};
};

struct ActuatorOutput {
    DiscreteCommand discrete{DiscreteCommand::Stop};
    float analog{0.0f};
    uint8_t winning_source_id{0};
    ArbitrationReason reason{ArbitrationReason::None};
};

template <size_t MaxSources = 8, uint32_t DeadtimeMs = 250>
class PriorityArbiter {
public:
    constexpr PriorityArbiter() = default;

    bool submit_request(uint8_t source_id,
                        PriorityLevel priority,
                        DiscreteCommand discrete_cmd,
                        float analog_setpoint,
                        uint32_t now_ms,
                        uint32_t ttl_ms) noexcept {
        auto* slot = find_or_allocate_slot(source_id);
        if (!slot) {
            return false;
        }

        slot->source_id = source_id;
        slot->priority = priority;
        slot->discrete_cmd = discrete_cmd;
        slot->analog_setpoint = std::clamp(analog_setpoint, 0.0f, 1.0f);
        slot->timestamp_ms = now_ms;
        slot->ttl_ms = ttl_ms;
        slot->is_active = true;
        return true;
    }

    void update(uint32_t now_ms, uint32_t dt_ms) noexcept {
        invalidate_expired(now_ms);

        const auto best_req = select_highest_priority();
        DiscreteCommand target_discrete = DiscreteCommand::Stop;
        float target_analog = 0.0f;
        ArbitrationReason target_reason = ArbitrationReason::None;
        uint8_t winner_id = 0;

        if (best_req) {
            target_discrete = best_req->discrete_cmd;
            target_analog = best_req->analog_setpoint;
            winner_id = best_req->source_id;

            switch (best_req->priority) {
                case PriorityLevel::Safety:     target_reason = ArbitrationReason::SafetyShutdown; break;
                case PriorityLevel::Protection: target_reason = ArbitrationReason::ProtectionTrip; break;
                case PriorityLevel::Manual:     target_reason = ArbitrationReason::ManualOverride; break;
                default:                        target_reason = ArbitrationReason::NormalAuto;     break;
            }
        }

        current_output_.winning_source_id = winner_id;

        // Обробка взаємного блокування та паузи Dead-Time
        if (in_deadtime_) {
            if (deadtime_timer_ms_ <= dt_ms) {
                in_deadtime_ = false;
                deadtime_timer_ms_ = 0;
                current_output_.discrete = pending_discrete_;
                current_output_.reason = target_reason;
            } else {
                deadtime_timer_ms_ -= dt_ms;
                current_output_.discrete = DiscreteCommand::Stop;
                current_output_.reason = ArbitrationReason::DeadtimeHold;
            }
        } else {
            const bool is_reversal =
                (current_output_.discrete == DiscreteCommand::Forward && target_discrete == DiscreteCommand::Reverse) ||
                (current_output_.discrete == DiscreteCommand::Reverse && target_discrete == DiscreteCommand::Forward);

            if (is_reversal) {
                in_deadtime_ = true;
                deadtime_timer_ms_ = DeadtimeMs;
                pending_discrete_ = target_discrete;
                current_output_.discrete = DiscreteCommand::Stop;
                current_output_.reason = ArbitrationReason::DeadtimeHold;
            } else {
                current_output_.discrete = target_discrete;
                current_output_.reason = target_reason;
            }
        }

        // Аналоговий вихід активний лише під час руху
        current_output_.analog = (current_output_.discrete == DiscreteCommand::Stop) ? 0.0f : target_analog;
    }

    [[nodiscard]] constexpr ActuatorOutput output() const noexcept {
        return current_output_;
    }

    [[nodiscard]] constexpr bool in_deadtime() const noexcept {
        return in_deadtime_;
    }

private:
    ActuatorRequest* find_or_allocate_slot(uint8_t source_id) noexcept {
        for (size_t i = 0; i < active_count_; ++i) {
            if (requests_[i].source_id == source_id) {
                return &requests_[i];
            }
        }
        if (active_count_ < MaxSources) {
            return &requests_[active_count_++];
        }
        return nullptr;
    }

    void invalidate_expired(uint32_t now_ms) noexcept {
        for (size_t i = 0; i < active_count_; ++i) {
            if (requests_[i].is_active && (now_ms - requests_[i].timestamp_ms > requests_[i].ttl_ms)) {
                requests_[i].is_active = false;
            }
        }
    }

    [[nodiscard]] std::optional<ActuatorRequest> select_highest_priority() const noexcept {
        const ActuatorRequest* best = nullptr;
        for (size_t i = 0; i < active_count_; ++i) {
            if (!requests_[i].is_active) continue;

            if (!best || requests_[i].priority > best->priority) {
                best = &requests_[i];
            }
        }
        if (best) {
            return *best;
        }
        return std::nullopt;
    }

    std::array<ActuatorRequest, MaxSources> requests_{};
    size_t active_count_{0};
    ActuatorOutput current_output_{};
    DiscreteCommand pending_discrete_{DiscreteCommand::Stop};
    uint32_t deadtime_timer_ms_{0};
    bool in_deadtime_{false};
};

} // namespace embedded::control
