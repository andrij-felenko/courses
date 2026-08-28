#include <cstdint>
#include <concepts>
#include <functional>
#include <algorithm>

enum class InterfaceEvent : uint8_t {
    None = 0,
    ReedShortTap,
    ReedLongHold,
    TouchPress,
    TouchRelease
};

enum class LedMode : uint8_t {
    Off = 0,
    Static,
    Heartbeat,
    BlinkFast
};

class SealedInterfaceController {
public:
    struct Config {
        uint32_t debounce_time_ms{30};
        uint32_t long_hold_time_ms{5000};
        int32_t  touch_hysteresis{120};
        uint8_t  baseline_alpha_shift{6};
    };

    using EventCallback = std::function<void(InterfaceEvent)>;

    explicit SealedInterfaceController(EventCallback cb, Config cfg = {})
        : callback_(std::move(cb)), cfg_(cfg) {}

    void tick(bool reed_pin, uint16_t touch_raw, uint32_t now_ms) noexcept {
        update_magnetic(reed_pin, now_ms);
        update_capacitive(touch_raw, now_ms);
        update_indicator();
    }

    void set_led_mode(LedMode mode, uint8_t target_brightness = 255) noexcept {
        led_mode_ = mode;
        target_brightness_ = target_brightness;
    }

    [[nodiscard]] uint8_t get_led_pwm() const noexcept {
        return current_brightness_;
    }

private:
    void update_magnetic(bool pin_level, uint32_t now_ms) noexcept {
        if (pin_level != reed_raw_state_) {
            reed_raw_state_ = pin_level;
            last_reed_edge_ms_ = now_ms;
        }

        if ((now_ms - last_reed_edge_ms_) >= cfg_.debounce_time_ms) {
            if (reed_raw_state_ != reed_debounced_state_) {
                reed_debounced_state_ = reed_raw_state_;

                if (reed_debounced_state_) {
                    press_start_ms_ = now_ms;
                    long_hold_triggered_ = false;
                } else {
                    if (!long_hold_triggered_ && (now_ms - press_start_ms_) >= cfg_.debounce_time_ms) {
                        dispatch(InterfaceEvent::ReedShortTap);
                    }
                }
            }
        }

        if (reed_debounced_state_ && !long_hold_triggered_) {
            if ((now_ms - press_start_ms_) >= cfg_.long_hold_time_ms) {
                long_hold_triggered_ = true;
                dispatch(InterfaceEvent::ReedLongHold);
            }
        }
    }

    void update_capacitive(uint16_t raw_counts, uint32_t now_ms) noexcept {
        if (baseline_fixed_ == 0) {
            baseline_fixed_ = static_cast<uint32_t>(raw_counts) << 16;
            return;
        }

        const auto baseline_val = static_cast<int32_t>(baseline_fixed_ >> 16);
        const int32_t delta = static_cast<int32_t>(raw_counts) - baseline_val;
        const bool touched_raw = (delta > cfg_.touch_hysteresis);

        if (touched_raw != is_touched_) {
            if (touch_debounce_ms_ == 0) {
                touch_debounce_ms_ = now_ms;
            } else if ((now_ms - touch_debounce_ms_) >= cfg_.debounce_time_ms) {
                is_touched_ = touched_raw;
                touch_debounce_ms_ = 0;
                dispatch(is_touched_ ? InterfaceEvent::TouchPress : InterfaceEvent::TouchRelease);
            }
        } else {
            touch_debounce_ms_ = 0;
        }

        if (!is_touched_) {
            const int32_t error = (static_cast<int32_t>(raw_counts) << 16) - static_cast<int32_t>(baseline_fixed_);
            baseline_fixed_ += (error >> cfg_.baseline_alpha_shift);
        }
    }

    void update_indicator() noexcept {
        ++phase_counter_;
        switch (led_mode_) {
            case LedMode::Off:
                current_brightness_ = 0;
                break;
            case LedMode::Static:
                current_brightness_ = target_brightness_;
                break;
            case LedMode::Heartbeat: {
                const uint16_t step = phase_counter_ % 256;
                current_brightness_ = static_cast<uint8_t>(step < 128 ? step * 2 : (255 - step) * 2);
                break;
            }
            case LedMode::BlinkFast:
                current_brightness_ = ((phase_counter_ % 32) < 16) ? 255 : 0;
                break;
        }
    }

    void dispatch(InterfaceEvent ev) const noexcept {
        if (callback_) {
            callback_(ev);
        }
    }

    EventCallback callback_;
    Config cfg_;

    // Magnetic state
    bool reed_raw_state_{false};
    bool reed_debounced_state_{false};
    bool long_hold_triggered_{false};
    uint32_t last_reed_edge_ms_{0};
    uint32_t press_start_ms_{0};

    // Capacitive state
    uint32_t baseline_fixed_{0};
    bool is_touched_{false};
    uint32_t touch_debounce_ms_{0};

    // LED state
    LedMode led_mode_{LedMode::Off};
    uint8_t current_brightness_{0};
    uint8_t target_brightness_{255};
    uint16_t phase_counter_{0};
};
