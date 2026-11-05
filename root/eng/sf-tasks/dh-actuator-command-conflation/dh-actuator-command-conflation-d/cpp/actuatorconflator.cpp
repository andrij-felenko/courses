#include <cstdint>
#include <array>
#include <optional>

template <size_t MaxActuators = 8>
class ActuatorConflator {
public:
    struct Command {
        uint32_t actuator_id{0};
        float target_value{0.0f};
        uint32_t timestamp_ms{0};
    };

    explicit ActuatorConflator(uint32_t cooldown_ms) : cooldown_ms_(cooldown_ms) {
        last_sent_time_.fill(0);
        last_sent_value_.fill(0.0f);
        slots_valid_.fill(false);
    }

    bool push(uint32_t actuator_id, float value, uint32_t now_ms) {
        if (actuator_id >= MaxActuators) return false;

        // Дедуплікація повторних ідентичних запитів
        if (slots_valid_[actuator_id] && last_sent_value_[actuator_id] == value) {
            ++suppressed_count_;
            return true;
        }

        // Latest-wins conflation: заміна проміжного значення
        if (slots_valid_[actuator_id]) {
            ++suppressed_count_;
        }

        slots_[actuator_id] = Command{actuator_id, value, now_ms};
        slots_valid_[actuator_id] = true;
        return true;
    }

    std::optional<float> pop_ready(uint32_t actuator_id, uint32_t now_ms) {
        if (actuator_id >= MaxActuators || !slots_valid_[actuator_id]) {
            return std::nullopt;
        }

        // Захист часовим інтервалом cooldown
        if ((now_ms - last_sent_time_[actuator_id]) < cooldown_ms_) {
            return std::nullopt;
        }

        float value = slots_[actuator_id].target_value;
        last_sent_time_[actuator_id] = now_ms;
        last_sent_value_[actuator_id] = value;
        slots_valid_[actuator_id] = false;
        return value;
    }

    [[nodiscard]] uint32_t get_suppressed_count() const noexcept {
        return suppressed_count_;
    }

private:
    uint32_t cooldown_ms_;
    std::array<Command, MaxActuators> slots_{};
    std::array<bool, MaxActuators> slots_valid_{};
    std::array<uint32_t, MaxActuators> last_sent_time_{};
    std::array<float, MaxActuators> last_sent_value_{};
    uint32_t suppressed_count_{0};
};
