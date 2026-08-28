#include <cstdint>
#include <string_view>
#include <array>
#include <chrono>
#include <optional>
#include <algorithm>

namespace embedded::alarm {

using namespace std::chrono_literals;

enum class Priority : uint8_t {
    Info     = 0,
    Warning  = 1,
    Critical = 2
};

enum class State : uint8_t {
    Normal,
    UnacknowledgedActive,
    AcknowledgedActive,
    UnacknowledgedCleared
};

struct AlarmConfig {
    std::string_view           name;
    Priority                   priority{Priority::Info};
    uint32_t                   parent_mask{0};
    std::chrono::milliseconds  on_delay{200ms};
    std::chrono::milliseconds  off_delay{500ms};
    std::chrono::milliseconds  escalation_timeout{60s};
};

template <size_t MaxAlarms = 32>
class AlarmManager {
public:
    constexpr AlarmManager() = default;

    std::optional<size_t> register_alarm(const AlarmConfig& config) noexcept {
        if (alarm_count_ >= MaxAlarms) {
            return std::nullopt;
        }
        size_t id = alarm_count_++;
        configs_[id] = config;
        states_[id]  = State::Normal;
        return id;
    }

    void update(size_t id, bool raw_condition, 
                std::chrono::milliseconds now, 
                std::chrono::milliseconds dt) noexcept {
        if (id >= alarm_count_) return;

        auto& cfg = configs_[id];
        auto& dyn = runtime_[id];

        // 1. Придушення за маскою батьківських тривог
        dyn.is_suppressed = (cfg.parent_mask & active_mask_) != 0;

        // 2. Деренчання
        if (now - dyn.last_transition >= 60s) {
            dyn.transition_count = 0;
        }

        // 3. Інтегратори дебаунсу
        if (raw_condition) {
            dyn.clear_timer = 0ms;
            dyn.active_timer += dt;
        } else {
            dyn.active_timer = 0ms;
            dyn.clear_timer += dt;
        }

        const bool debounced_active = (dyn.active_timer >= cfg.on_delay);
        const bool debounced_clear  = (dyn.clear_timer >= cfg.off_delay);

        // 4. Автомат життєвого циклу
        switch (states_[id]) {
            case State::Normal:
                if (debounced_active && !dyn.is_suppressed) {
                    states_[id] = State::UnacknowledgedActive;
                    dyn.transition_count++;
                    dyn.last_transition = now;
                }
                break;

            case State::UnacknowledgedActive:
                if (debounced_clear) {
                    states_[id] = State::UnacknowledgedCleared;
                }
                break;

            case State::AcknowledgedActive:
                if (debounced_clear) {
                    states_[id] = State::Normal;
                    dyn.ack_timestamp = 0ms;
                } else if (cfg.escalation_timeout > 0ms && 
                          (now - dyn.ack_timestamp >= cfg.escalation_timeout)) {
                    states_[id] = State::UnacknowledgedActive;
                    audio_silenced_ = false;
                }
                break;

            case State::UnacknowledgedCleared:
                if (debounced_active && !dyn.is_suppressed) {
                    states_[id] = State::UnacknowledgedActive;
                }
                break;
        }

        if (dyn.transition_count >= 3) {
            dyn.is_chattering = true;
        }

        // Оновлення бітових масок
        const uint32_t bit = (1U << id);
        if (states_[id] == State::UnacknowledgedActive || states_[id] == State::AcknowledgedActive) {
            active_mask_ |= bit;
        } else {
            active_mask_ &= ~bit;
        }
    }

    void acknowledge(size_t id, std::chrono::milliseconds now) noexcept {
        if (id >= alarm_count_) return;
        if (states_[id] == State::UnacknowledgedActive) {
            states_[id] = State::AcknowledgedActive;
            runtime_[id].ack_timestamp = now;
        } else if (states_[id] == State::UnacknowledgedCleared) {
            states_[id] = State::Normal;
        }
    }

    void silence() noexcept {
        audio_silenced_ = true;
    }

    [[nodiscard]] std::optional<Priority> highest_unack_priority() const noexcept {
        std::optional<Priority> max_prio;
        for (size_t i = 0; i < alarm_count_; ++i) {
            if (states_[i] == State::UnacknowledgedActive && !runtime_[i].is_suppressed) {
                if (!max_prio || configs_[i].priority > *max_prio) {
                    max_prio = configs_[i].priority;
                }
            }
        }
        return audio_silenced_ ? std::nullopt : max_prio;
    }

    [[nodiscard]] State get_state(size_t id) const noexcept {
        return (id < alarm_count_) ? states_[id] : State::Normal;
    }

private:
    struct RuntimeState {
        std::chrono::milliseconds active_timer{0ms};
        std::chrono::milliseconds clear_timer{0ms};
        std::chrono::milliseconds ack_timestamp{0ms};
        std::chrono::milliseconds last_transition{0ms};
        uint8_t                   transition_count{0};
        bool                      is_suppressed{false};
        bool                      is_chattering{false};
    };

    std::array<AlarmConfig, MaxAlarms>  configs_{};
    std::array<State, MaxAlarms>        states_{};
    std::array<RuntimeState, MaxAlarms> runtime_{};
    size_t                              alarm_count_{0};
    uint32_t                            active_mask_{0};
    bool                                audio_silenced_{false};
};

} // namespace embedded::alarm
