#pragma once

#include <algorithm>
#include <cstdint>
#include <string>

namespace bumpless {

// Прапорці телеметрії: чому саме регулятор не гарантує безривковості.
enum class Fault : std::uint32_t {
    None = 0,
    BadMeasurement = 1u << 0,  // NaN/Inf з давача або з приводу
    BadDt = 1u << 1,           // dt <= 0, NaN або проґавлений такт
    PreloadClamped = 1u << 2,  // передзавантаження зрізане межею
    NotReady = 1u << 3,        // update() до handover()
    OutputSaturated = 1u << 4  // вихід стоїть на упорі приводу
};

[[nodiscard]] constexpr Fault operator|(Fault a, Fault b) noexcept
{
    return static_cast<Fault>(static_cast<std::uint32_t>(a) | static_cast<std::uint32_t>(b));
}

constexpr Fault& operator|=(Fault& a, Fault b) noexcept
{
    a = a | b;
    return a;
}

[[nodiscard]] constexpr bool contains(Fault set, Fault flag) noexcept
{
    return (static_cast<std::uint32_t>(set) & static_cast<std::uint32_t>(flag)) != 0u;
}

[[nodiscard]] std::string describe(Fault faults);

// Пауза, довша за цю, — це вже не джитер планувальника, а втрачений такт.
inline constexpr float kMaxDt = 0.20f;

struct PidConfig {
    float kp{0.0f};                 // од. приводу на од. виміру
    float ki{0.0f};
    float kd{0.0f};
    float kff{0.0f};                // пряме прогнозне керування від уставки
    float out_min{-1.0f};
    float out_max{1.0f};
    float i_min{-1.0f};
    float i_max{1.0f};
    float slew_rate_max{0.0f};      // темп зміни уставки [од/с], 0 = без ремпінгу
    float d_lpf_tau{0.0f};          // стала часу фільтра похідної, 0 = без фільтра
    float max_expected_noise{0.0f}; // розмах шуму виміру — резерв для P

    struct Limits {
        float lo{0.0f};
        float hi{0.0f};
    };

    // Межі інтегратора із запасом на пропорційне реагування:
    // I_max_safe = out_max - kp * max_expected_noise (і симетрично знизу).
    [[nodiscard]] constexpr Limits safe_integral_limits() const noexcept
    {
        const float margin = kp * max_expected_noise;
        float lo = std::max(i_min, out_min + margin);
        float hi = std::min(i_max, out_max - margin);
        if (lo > hi) {
            // Запас ширший за весь хід приводу: коефіцієнти нереальні.
            // Межі не вивертаємо — стягуємо в точку.
            const float mid = 0.5f * (lo + hi);
            lo = mid;
            hi = mid;
        }
        return Limits{lo, hi};
    }
};

// ПІД-регулятор із безривковою передачею повноважень. Не виділяє пам'яті,
// не кидає винятків і не має циклів зі змінною кількістю ітерацій, тож
// придатний до виклику просто з переривання контуру керування.
class BumplessPidController {
public:
    constexpr explicit BumplessPidController(const PidConfig& config) noexcept
        : cfg_{config}
    {
    }

    void set_target(float target) noexcept { target_setpoint_ = target; }

    // Безривкове захоплення: уставка сідає на поточний вимір, тому P(0+) = 0.
    void handover(float current_measurement, float target_setpoint,
                  float prev_actuator_output) noexcept;

    // Узагальнений випадок: оператор вимагає тримати конкретну точку, тому
    // P(0+) != 0 і його теж треба відняти від передзавантаження.
    void handover_hold(float current_measurement, float hold_setpoint,
                       float target_setpoint, float prev_actuator_output) noexcept;

    // Наївний старт «з чистого аркуша» — лишено для демонстрації удару.
    void start_naive(float setpoint) noexcept;

    void reset() noexcept;

    [[nodiscard]] float update(float measurement, float dt) noexcept;

    [[nodiscard]] float last_output() const noexcept { return last_output_; }
    [[nodiscard]] float integral() const noexcept { return integral_; }
    [[nodiscard]] float current_setpoint() const noexcept { return current_setpoint_; }
    [[nodiscard]] bool ready() const noexcept { return is_initialized_; }
    [[nodiscard]] Fault faults() const noexcept { return faults_; }
    void clear_faults() noexcept { faults_ = Fault::None; }

private:
    void preload(float measurement, float hold_setpoint, float target_setpoint,
                 float prev_output) noexcept;

    PidConfig cfg_{};
    float integral_{0.0f};
    float prev_measurement_{0.0f}; // пам'ять диференціатора: похідна ВИМІРУ
    float deriv_filt_{0.0f};
    float target_setpoint_{0.0f};  // кінцева ціль місії
    float current_setpoint_{0.0f}; // уставка після ремпінгу
    float last_output_{0.0f};
    bool is_initialized_{false};
    Fault faults_{Fault::None};
};

} // namespace bumpless
