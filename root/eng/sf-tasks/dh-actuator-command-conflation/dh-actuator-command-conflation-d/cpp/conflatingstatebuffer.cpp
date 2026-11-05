#include <cstdint>
#include <array>
#include <optional>

template <size_t MaxActuators = 16>
class ConflatingStateBuffer {
public:
    struct Slot {
        uint32_t actuator_id{0};
        float target_value{0.0f};
        uint32_t timestamp_ms{0};
        bool is_occupied{false};
    };

    explicit ConflatingStateBuffer(uint32_t cooldown_ms) noexcept
        : cooldown_ms_(cooldown_ms) {
        last_dispatch_time_.fill(0);
        last_dispatch_value_.fill(0.0f);
        has_dispatched_.fill(false);
    }

    bool push(uint32_t actuator_id, float value, uint32_t now_ms) noexcept {
        if (actuator_id >= MaxActuators) {
            return false;
        }

        // Пригнічення дублікатів щодо останнього відправленого стану
        if (has_dispatched_[actuator_id] && last_dispatch_value_[actuator_id] == value) {
            ++suppressed_count_;
            return true;
        }

        // Витіснення застарілого незчитаного стану (latest-wins)
        if (slots_[actuator_id].is_occupied) {
            ++suppressed_count_;
        }

        slots_[actuator_id] = Slot{actuator_id, value, now_ms, true};
        return true;
    }

    std::optional<float> pop_ready(uint32_t actuator_id, uint32_t now_ms) noexcept {
        if (actuator_id >= MaxActuators || !slots_[actuator_id].is_occupied) {
            return std::nullopt;
        }

        // Перевірка дотримання часового інтервалу cooldown
        if (has_dispatched_[actuator_id]) {
            uint32_t elapsed = now_ms - last_dispatch_time_[actuator_id];
            if (elapsed < cooldown_ms_) {
                return std::nullopt;
            }
        }

        float value = slots_[actuator_id].target_value;
        last_dispatch_time_[actuator_id] = now_ms;
        last_dispatch_value_[actuator_id] = value;
        has_dispatched_[actuator_id] = true;
        slots_[actuator_id].is_occupied = false;
        return value;
    }

    [[nodiscard]] uint32_t get_suppressed_count() const noexcept {
        return suppressed_count_;
    }

private:
    uint32_t cooldown_ms_;
    std::array<Slot, MaxActuators> slots_{};
    std::array<uint32_t, MaxActuators> last_dispatch_time_{};
    std::array<float, MaxActuators> last_dispatch_value_{};
    std::array<bool, MaxActuators> has_dispatched_{};
    uint32_t suppressed_count_{0};
};
