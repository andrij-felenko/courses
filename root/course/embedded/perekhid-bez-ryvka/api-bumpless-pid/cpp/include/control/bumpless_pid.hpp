#pragma once

/*
 * Безривковий ПІД-регулятор для вбудованих систем реального часу.
 *
 * Клас не виділяє пам'яті, не кидає винятків і не блокується;
 * час виконання кожного методу сталий.
 */

#include <cstdint>
#include <functional>

namespace control {

/*
 * Конфігураційні коефіцієнти контуру.
 *
 * Об'єкт лише читається, тож його оголошують `constexpr`/`const`
 * і кладуть у Flash/ROM: регулятор тримає ПОСИЛАННЯ на нього,
 * тому одна конфігурація обслуговує кілька осей.
 */
struct PidConfig {
    float kp{0.0f};              ///< [од. приводу / од. виміру]
    float ki{0.0f};              ///< [од. приводу / (од. виміру·с)]
    float kd{0.0f};              ///< [од. приводу·с / од. виміру]
    float kff{0.0f};             ///< прямий модельний зв'язок (Feedforward)
    float out_min{-1.0f};        ///< нижня фізична межа виходу приводу
    float out_max{1.0f};         ///< верхня фізична межа виходу приводу
    float i_min{-1.0f};          ///< межі інтегратора (anti-windup clamping)
    float i_max{1.0f};
    float slew_rate_max{0.0f};   ///< [од/с], 0 = ремпінг вимкнено
};

/// Чи придатна конфігурація: межі не перевернуті, коефіцієнти скінченні.
[[nodiscard]] bool is_sane(const PidConfig& config) noexcept;

/// Прапорці останнього такту.
enum class PidFlag : std::uint8_t {
    None = 0,
    Saturated = 1u << 0,        ///< вихід уперся в out_min/out_max
    IntegralClamped = 1u << 1,  ///< інтегратор уперся в i_min/i_max
    IntegralHeld = 1u << 2,     ///< інтегрування зупинено анти-віндапом
    SensorFault = 1u << 3,      ///< вимір не є скінченним числом
    InvalidDt = 1u << 4,        ///< dt <= 0 або не скінченне
    Slewing = 1u << 5,          ///< уставка обмежена темпом наростання
    Fresh = 1u << 6             ///< службовий: такт одразу після handover
};

[[nodiscard]] constexpr PidFlag operator|(PidFlag a, PidFlag b) noexcept
{
    return static_cast<PidFlag>(static_cast<std::uint8_t>(a) |
                                static_cast<std::uint8_t>(b));
}

[[nodiscard]] constexpr PidFlag operator&(PidFlag a, PidFlag b) noexcept
{
    return static_cast<PidFlag>(static_cast<std::uint8_t>(a) &
                                static_cast<std::uint8_t>(b));
}

constexpr PidFlag& operator|=(PidFlag& a, PidFlag b) noexcept
{
    a = a | b;
    return a;
}

[[nodiscard]] constexpr bool holds(PidFlag set, PidFlag bit) noexcept
{
    return (set & bit) != PidFlag::None;
}

/*
 * Знімок внутрішніх доданків за такт — для телеметрії й налагодження.
 * Регулятор його не зберігає: структуру дає викликова сторона.
 */
struct PidTelemetry {
    float setpoint{0.0f};
    float measurement{0.0f};
    float error{0.0f};
    float p_term{0.0f};
    float i_term{0.0f};
    float d_term{0.0f};
    float ff_term{0.0f};
    float output{0.0f};
    PidFlag flags{PidFlag::None};
};

/*
 * Один контур керування. Розмір екземпляра на 32-бітному ядрі — 32 байти:
 * посилання 4 + п'ять float 20 + лічильник збоїв 4 + прапорці й стан 4.
 */
class BumplessPidController {
public:
    explicit BumplessPidController(const PidConfig& config) noexcept;

    /*
     * Безривкова передача повноважень. Викликається одноразово в момент
     * зміни активного режиму — тим самим свіжим відліком, що піде в update.
     */
    void handover(float current_measurement,
                  float target_setpoint,
                  float prev_actuator_output) noexcept;

    /// Один крок замкненого контуру.
    [[nodiscard]] float update(float measurement, float dt) noexcept;

    /// Те саме з викладенням доданків у знімок телеметрії.
    [[nodiscard]] float update(float measurement, float dt,
                               PidTelemetry& trace) noexcept;

    /// Зміна цільової уставки на льоту; до неї веде обмежувач швидкості.
    void set_target(float target) noexcept { target_setpoint_ = target; }

    [[nodiscard]] float output() const noexcept { return last_output_; }
    [[nodiscard]] float integral() const noexcept { return integral_; }
    [[nodiscard]] float setpoint() const noexcept { return current_setpoint_; }
    [[nodiscard]] bool is_initialized() const noexcept { return initialized_; }
    [[nodiscard]] std::uint32_t fault_count() const noexcept { return fault_count_; }

    /// Прапорці останнього такту без службового біта Fresh.
    [[nodiscard]] PidFlag flags() const noexcept;

private:
    float step(float measurement, float dt, PidTelemetry* trace) noexcept;
    void freeze(PidTelemetry* trace, float measurement, PidFlag flags) const noexcept;

    std::reference_wrapper<const PidConfig> cfg_;
    float integral_{0.0f};
    float prev_measurement_{0.0f};
    float target_setpoint_{0.0f};
    float current_setpoint_{0.0f};
    float last_output_{0.0f};
    std::uint32_t fault_count_{0};
    PidFlag flags_{PidFlag::None};
    bool initialized_{false};
};

} // namespace control
