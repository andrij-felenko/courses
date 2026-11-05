#include <cstdint>
#include <algorithm>
#include <atomic>

namespace EmbeddedControl {

enum class Mode : uint8_t {
    Blending,
    WinnerTakeAll
};

template<typename T = int32_t>
class FixedPointQ16 {
public:
    static constexpr int32_t Shift = 16;
    static constexpr int32_t One = 1 << Shift;

    constexpr FixedPointQ16() : raw_value_(0) {}
    constexpr explicit FixedPointQ16(int32_t raw) : raw_value_(raw) {}

    static constexpr FixedPointQ16 from_fraction(int32_t num, int32_t den) {
        return FixedPointQ16(static_cast<int32_t>((static_cast<int64_t>(num) << Shift) / den));
    }

    constexpr int32_t raw() const { return raw_value_; }

    constexpr FixedPointQ16 operator+(FixedPointQ16 rhs) const {
        return FixedPointQ16(raw_value_ + rhs.raw_value_);
    }

    constexpr FixedPointQ16 operator-(FixedPointQ16 rhs) const {
        return FixedPointQ16(raw_value_ - rhs.raw_value_);
    }

    constexpr FixedPointQ16 operator*(FixedPointQ16 rhs) const {
        int64_t prod = static_cast<int64_t>(raw_value_) * rhs.raw_value_;
        return FixedPointQ16(static_cast<int32_t>(prod >> Shift));
    }

private:
    int32_t raw_value_;
};

class ArbitrationEngine {
public:
    struct Configuration {
        int32_t max_slew_rate_q16;
        int32_t min_limit_q16;
        int32_t max_limit_q16;
        int32_t hyst_high_q16;
        int32_t hyst_low_q16;
    };

    explicit ArbitrationEngine(const Configuration& config)
        : config_(config), current_mode_(Mode::Blending), last_output_q16_(0) {}

    int32_t update(int32_t primary_cmd, int32_t secondary_cmd, int32_t weight_q16) {
        // Оновлення гістерезисного стану
        if (current_mode_ == Mode::Blending && weight_q16 >= config_.hyst_high_q16) {
            current_mode_ = Mode::WinnerTakeAll;
        } else if (current_mode_ == Mode::WinnerTakeAll && weight_q16 < config_.hyst_low_q16) {
            current_mode_ = Mode::Blending;
        }

        int32_t raw_out = 0;
        if (current_mode_ == Mode::WinnerTakeAll) {
            raw_out = primary_cmd;
        } else {
            // Опукла комбінація: y = u2 + w * (u1 - u2)
            int64_t diff = static_cast<int64_t>(primary_cmd) - secondary_cmd;
            int32_t scaled_diff = static_cast<int32_t>((diff * weight_q16) >> 16);
            raw_out = secondary_cmd + scaled_diff;
        }

        // Обмежувач швидкості зміни
        int32_t delta = raw_out - last_output_q16_;
        if (delta > config_.max_slew_rate_q16) {
            raw_out = last_output_q16_ + config_.max_slew_rate_q16;
        } else if (delta < -config_.max_slew_rate_q16) {
            raw_out = last_output_q16_ - config_.max_slew_rate_q16;
        }

        // Проектор меж безпеки
        raw_out = std::clamp(raw_out, config_.min_limit_q16, config_.max_limit_q16);

        last_output_q16_ = raw_out;
        return raw_out;
    }

    Mode mode() const { return current_mode_; }

private:
    Configuration config_;
    Mode current_mode_;
    int32_t last_output_q16_;
};

} // namespace EmbeddedControl
