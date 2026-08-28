#include <cstdint>

template <std::uint8_t StabilityThreshold = 15>
class ContactDebounceFilter {
public:
    constexpr ContactDebounceFilter() = default;

    // Періодична обробка вибірки у таймерному перериванні
    bool process_sample(bool raw_input_pin) noexcept {
        if (raw_input_pin != stable_state_) {
            if (++sample_counter_ >= StabilityThreshold) {
                stable_state_ = raw_input_pin;
                sample_counter_ = 0;
            }
        } else {
            sample_counter_ = 0;
        }
        return stable_state_;
    }

    [[nodiscard]] constexpr bool get_state() const noexcept {
        return stable_state_;
    }

private:
    std::uint8_t sample_counter_{0};
    bool stable_state_{false};
};
