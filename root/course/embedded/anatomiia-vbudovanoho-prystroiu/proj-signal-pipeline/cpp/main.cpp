#include <cstdint>
#include <algorithm>

constexpr uint32_t kAdcMaxCode = 4095;
constexpr uint32_t kAdcVrefMv  = 3300;
constexpr uint16_t kPwmMaxDuty = 65535;

/* Клас експоненційного фільтра без динамічної пам'яті */
template <uint8_t ShiftK = 3>
class EmaFilter {
public:
    constexpr EmaFilter() noexcept = default;

    int32_t update(int32_t new_val) noexcept {
        if (!initialized_) {
            filtered_val_ = new_val;
            initialized_ = true;
            return new_val;
        }
        filtered_val_ += (new_val - filtered_val_) >> ShiftK;
        return filtered_val_;
    }

    [[nodiscard]] int32_t value() const noexcept { return filtered_val_; }
    void reset() noexcept { initialized_ = false; filtered_val_ = 0; }

private:
    int32_t filtered_val_{0};
    bool initialized_{false};
};

/* Клас дискретного цілочисельного ПІД-регулятора */
class PidController {
public:
    constexpr PidController(int32_t kp_q8, int32_t ki_q8, int32_t kd_q8,
                            int32_t out_min, int32_t out_max) noexcept
        : kp_(kp_q8), ki_(ki_q8), kd_(kd_q8),
          out_min_(out_min), out_max_(out_max) {}

    int32_t update(int32_t setpoint, int32_t measured) noexcept {
        const int32_t error = setpoint - measured;

        const int32_t p_term = (kp_ * error) >> 8;

        integral_accum_ += error;
        int32_t i_term = (ki_ * integral_accum_) >> 8;

        /* Захист від інтегрального насичення (Anti-Windup) */
        if (i_term > out_max_) {
            i_term = out_max_;
            integral_accum_ = (out_max_ << 8) / (ki_ > 0 ? ki_ : 1);
        } else if (i_term < out_min_) {
            i_term = out_min_;
            integral_accum_ = (out_min_ << 8) / (ki_ > 0 ? ki_ : 1);
        }

        const int32_t derivative = error - prev_error_;
        const int32_t d_term = (kd_ * derivative) >> 8;
        prev_error_ = error;

        const int32_t output = p_term + i_term + d_term;
        return std::clamp(output, out_min_, out_max_);
    }

    void reset() noexcept {
        integral_accum_ = 0;
        prev_error_ = 0;
    }

private:
    int32_t kp_;
    int32_t ki_;
    int32_t kd_;
    int32_t integral_accum_{0};
    int32_t prev_error_{0};
    int32_t out_min_;
    int32_t out_max_;
};

/* Наскрізний клас обробного конвеєра */
class SignalPipeline {
public:
    explicit SignalPipeline(PidController pid) noexcept : pid_(pid) {}

    uint16_t process(uint16_t raw_adc, uint16_t target_mv) noexcept {
        /* 1. Масштабування відліку АЦП */
        const uint32_t mv_raw = (static_cast<uint32_t>(raw_adc) * kAdcVrefMv) / kAdcMaxCode;

        /* 2. Цифрова фільтрація */
        const int32_t mv_filt = filter_.update(static_cast<int32_t>(mv_raw));

        /* 3. Розрахунок ПІД-регулятора */
        const int32_t control = pid_.update(static_cast<int32_t>(target_mv), mv_filt);

        /* 4. Формування сигналу керування ШІМ */
        const int32_t clamped_duty = std::clamp<int32_t>(control, 0, kPwmMaxDuty);
        return static_cast<uint16_t>(clamped_duty);
    }

private:
    EmaFilter<3> filter_{};
    PidController pid_;
};
