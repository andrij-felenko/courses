#include <cstdint>
#include <array>
#include <algorithm>
#include <chrono>

enum class HysteresisMode : uint8_t {
    Heating, // Активний низький: УВІМК при T <= Low, ВИМК при T >= High
    Cooling  // Активний високий: УВІМК при T >= High, ВИМК при T <= Low
};

template <typename ValueType = float, size_t WindowSize = 5>
class HysteresisGate {
    static_assert(WindowSize >= 3 && WindowSize % 2 == 1, "WindowSize must be odd and >= 3");

public:
    struct Settings {
        ValueType threshold_low;
        ValueType threshold_high;
        std::chrono::milliseconds min_on_time;
        std::chrono::milliseconds min_off_time;
        ValueType ema_alpha{static_cast<ValueType>(0.25)};
        HysteresisMode mode{HysteresisMode::Heating};
    };

    explicit HysteresisGate(Settings settings, std::chrono::milliseconds start_time = std::chrono::milliseconds{0})
        : settings_(settings), last_change_(start_time) {}

    bool process(ValueType sample, std::chrono::milliseconds current_time) {
        // 1. Медіанний фільтр
        window_[head_] = sample;
        head_ = (head_ + 1) % WindowSize;
        if (count_ < WindowSize) ++count_;

        std::array<ValueType, WindowSize> sorted{};
        std::copy_n(window_.begin(), count_, sorted.begin());
        std::sort(sorted.begin(), sorted.begin() + count_);
        const ValueType median_val = sorted[count_ / 2];

        // 2. Фільтр EMA
        if (!initialized_) {
            filtered_val_ = median_val;
            initialized_ = true;
        } else {
            filtered_val_ = settings_.ema_alpha * median_val + (static_cast<ValueType>(1) - settings_.ema_alpha) * filtered_val_;
        }

        // 3. Часове блокування Hold-off
        const auto time_in_state = current_time - last_change_;
        const auto hold_limit = is_active_ ? settings_.min_on_time : settings_.min_off_time;
        if (time_in_state < hold_limit) {
            return is_active_;
        }

        // 4. Двопороговий тригер
        bool next_state = is_active_;
        if (settings_.mode == HysteresisMode::Heating) {
            if (filtered_val_ <= settings_.threshold_low) {
                next_state = true;
            } else if (filtered_val_ >= settings_.threshold_high) {
                next_state = false;
            }
        } else {
            if (filtered_val_ >= settings_.threshold_high) {
                next_state = true;
            } else if (filtered_val_ <= settings_.threshold_low) {
                next_state = false;
            }
        }

        if (next_state != is_active_) {
            is_active_ = next_state;
            last_change_ = current_time;
        }

        return is_active_;
    }

    [[nodiscard]] bool is_active() const noexcept { return is_active_; }
    [[nodiscard]] ValueType filtered_value() const noexcept { return filtered_val_; }

private:
    Settings settings_;
    std::array<ValueType, WindowSize> window_{};
    size_t head_{0};
    size_t count_{0};
    ValueType filtered_val_{0};
    bool initialized_{false};
    bool is_active_{false};
    std::chrono::milliseconds last_change_{0};
};
