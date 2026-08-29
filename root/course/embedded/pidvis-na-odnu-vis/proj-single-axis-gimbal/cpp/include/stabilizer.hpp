// stabilizer.hpp — математика контуру: фільтр, ПІД, калібрування, мапування.
//
// Заголовок без .cpp навмисно: тут немає жодного звертання до заліза, усе
// придатне до constexpr і до прогону на настільному комп'ютері записом
// зі стенда. Саме цей файл відповідає числовому простеженню в статті.

#pragma once

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <optional>
#include <span>

#include "servo.hpp"

namespace gimbal {

inline constexpr float kDtSec       = 0.005f;  // такт 200 Гц
inline constexpr float kMaxAngleDeg = 45.0f;   // механічна межа шарніра
inline constexpr float kMaxBiasVar  = 0.25f;   // (°/с)² — поріг спокою
inline constexpr float kPi          = 3.14159265f;

[[nodiscard]] inline float tilt_from_accel(float ay, float az) noexcept {
    return std::atan2(ay, az) * (180.0f / kPi);
}

// ---------------------------------------------------------- комплементарний фільтр

class ComplementaryFilter {
public:
    explicit constexpr ComplementaryFilter(float alpha) noexcept : alpha_{alpha} {}

    float update(float rate_dps, float ay, float az, float dt) noexcept {
        // Гіроскоп задає форму (швидко, але спливає),
        // акселерометр тягне до істини (повільно, зате без дрейфу).
        const float predicted = angle_deg_ + rate_dps * dt;
        angle_deg_ = alpha_ * predicted + (1.0f - alpha_) * tilt_from_accel(ay, az);
        return angle_deg_;
    }

    // Початкове наведення на акселерометр: стенд може стояти під нахилом,
    // і фільтру не треба повзти до істини від нуля цілу секунду.
    void seed(float ay, float az) noexcept { angle_deg_ = tilt_from_accel(ay, az); }

    [[nodiscard]] constexpr float angle() const noexcept { return angle_deg_; }

private:
    float alpha_;
    float angle_deg_{0.0f};
};

// ------------------------------------------------------------------------- ПІД

class Pid {
public:
    struct Config {
        float kp{2.0f};
        float ki{0.5f};
        float kd{0.08f};
        float out_min{-kMaxAngleDeg};
        float out_max{kMaxAngleDeg};
        float d_cutoff_hz{25.0f};   // вище смуги контуру, нижче вібрації мотора
        float deadband_deg{0.3f};   // проти дребезгу на люфті редуктора
    };

    explicit Pid(const Config& cfg) noexcept : cfg_{cfg} {
        // ФНЧ 1-го порядку: beta = dt / (dt + RC), RC = 1/(2*pi*fc).
        if (cfg_.d_cutoff_hz > 0.0f) {
            const float rc = 1.0f / (2.0f * kPi * cfg_.d_cutoff_hz);
            d_lpf_alpha_ = kDtSec / (kDtSec + rc);
        }
    }

    [[nodiscard]] float update(float setpoint_deg, float angle_deg,
                               float measured_rate_dps, float dt) noexcept {
        float error = setpoint_deg - angle_deg;

        // Мертва зона: люфт редуктора й нечутливість потенціометра серво
        // роблять дрібну похибку невідпрацьовуваною, а контур на ній гріється.
        if (std::abs(error) < cfg_.deadband_deg) {
            error = 0.0f;
        }

        const float p_term = cfg_.kp * error;

        // Похідна за ВИМІРОМ, а не за похибкою: джерело швидкості — гіроскоп.
        d_lpf_state_ += d_lpf_alpha_ * (-measured_rate_dps - d_lpf_state_);
        const float d_term = cfg_.kd * d_lpf_state_;

        // Пробний вихід зі СТАРИМ інтегралом — за ним судимо про насичення.
        const float tentative = p_term + integrator_ + d_term;

        const bool saturated = (tentative > cfg_.out_max) || (tentative < cfg_.out_min);
        const bool pushes_further = (tentative * error > 0.0f);

        // Clamping anti-windup: коли вихід уперся, а похибка тягне туди ж,
        // інтегрувати нікуди — приріст лише накопичив би борг на розворот.
        if (!saturated || !pushes_further) {
            integrator_ += cfg_.ki * error * dt;
        }
        integrator_ = std::clamp(integrator_, cfg_.out_min, cfg_.out_max);

        return std::clamp(p_term + integrator_ + d_term, cfg_.out_min, cfg_.out_max);
    }

    void reset() noexcept {
        integrator_  = 0.0f;
        d_lpf_state_ = 0.0f;
    }

    [[nodiscard]] constexpr float integrator() const noexcept { return integrator_; }

private:
    Config cfg_;
    float  integrator_{0.0f};
    float  d_lpf_state_{0.0f};
    float  d_lpf_alpha_{1.0f};
};

// ------------------------------------------------------------- калібрування нуля

// Онлайновий Велфорд: середнє й дисперсію 500 вибірок рахуємо трьома
// числами. Масив на 500 float — це 2000 байтів при 2048 байтах SRAM
// усього мікроконтролера, тобто ніяк.
class GyroCalibrator {
public:
    void reset() noexcept {
        count_ = 0;
        mean_  = 0.0f;
        m2_    = 0.0f;
    }

    void push(float gyro_dps) noexcept {
        ++count_;
        const float delta = gyro_dps - mean_;
        mean_ += delta / static_cast<float>(count_);
        m2_   += delta * (gyro_dps - mean_);
    }

    // Порожньо, якщо вибірок мало або давач рухався: стартувати з невідомим
    // зсувом не можна — кут поїде за хвилину.
    [[nodiscard]] std::optional<float> finish(std::uint16_t need_samples) const noexcept {
        if (count_ < need_samples || count_ < 2) {
            return std::nullopt;
        }
        const float variance = m2_ / static_cast<float>(count_ - 1);

        // Через «не більше» — так відсіюється й NaN зі сміття побитої шини.
        if (!(variance <= kMaxBiasVar)) {
            return std::nullopt;
        }
        return mean_;
    }

private:
    std::uint16_t count_{0};
    float         mean_{0.0f};
    float         m2_{0.0f};
};

// ------------------------------------------------------------------ стабілізатор

struct ControlOutput {
    float        angle_deg{0.0f};
    float        rate_dps{0.0f};
    float        correction_deg{0.0f};
    float        integrator{0.0f};
    Microseconds pulse{RcServo::kMid};
};

class Stabilizer {
public:
    Stabilizer(float filter_alpha, const Pid::Config& pid_cfg) noexcept
        : filter_{filter_alpha}, pid_{pid_cfg} {}

    void set_bias(float bias_dps) noexcept {
        gyro_bias_dps_ = bias_dps;
        calibrated_    = true;
    }

    void seed_angle(float ay, float az) noexcept { filter_.seed(ay, az); }

    // Скидає лише керувальний стан; калібрування й оцінка кута чинні далі.
    void reset_control() noexcept { pid_.reset(); }

    [[nodiscard]] ControlOutput step(float raw_gyro_dps, float ay, float az) noexcept {
        const float rate  = raw_gyro_dps - gyro_bias_dps_;
        const float angle = filter_.update(rate, ay, az, kDtSec);

        // Уставка стабілізатора горизонту незмінна — нуль.
        const float correction = pid_.update(0.0f, angle, rate, kDtSec);

        return ControlOutput{angle, rate, correction, pid_.integrator(),
                             pulse_from_angle(correction)};
    }

    [[nodiscard]] bool calibrated() const noexcept { return calibrated_; }

    // [-45°, +45°] → [1000, 2000] мкс, нуль у 1500 мкс.
    [[nodiscard]] static constexpr Microseconds pulse_from_angle(float deg) noexcept {
        constexpr float us_per_deg =
            static_cast<float>(RcServo::kMax.value - RcServo::kMin.value) /
            (2.0f * kMaxAngleDeg);

        const float raw = static_cast<float>(RcServo::kMid.value) + deg * us_per_deg;
        const float clamped = std::clamp(raw,
                                         static_cast<float>(RcServo::kMin.value),
                                         static_cast<float>(RcServo::kMax.value));
        return Microseconds{static_cast<std::uint16_t>(clamped + 0.5f)};
    }

private:
    ComplementaryFilter filter_;
    Pid                 pid_;
    float               gyro_bias_dps_{0.0f};
    bool                calibrated_{false};
};

}  // namespace gimbal
