/*
 * Демонстрація безривкової передачі повноважень.
 *
 * Сценарій одного польоту:
 *   0.0 с — ручний режим, пілот тримає фіксований хід газу;
 *   1.0 с — перемикання в утримання швидкості набору (handover);
 *   4.0 с — зрив обміну з давачем на 150 мс (NaN у вимірі);
 *   5.0 с — недосяжна ціль: привід у насиченні, працює анти-віндап;
 *   8.0 с — повернення цілі в межі досяжного.
 */
#include "control/bumpless_pid.hpp"
#include "control/numeric.hpp"
#include "control/plant.hpp"

#include <array>
#include <cmath>
#include <format>
#include <iostream>
#include <string>
#include <string_view>

namespace {

constexpr float kDt = 0.005f;   // 200 Гц — типовий такт контуру швидкості
constexpr float kSwitchAt = 1.0f;
constexpr float kFaultFrom = 4.0f;
constexpr float kFaultTo = 4.15f;
constexpr float kDemandAt = 5.0f;
constexpr float kRelaxAt = 8.0f;
constexpr float kEndAt = 12.0f;
constexpr float kPrintPeriod = 0.5f;

constexpr float kManualThrottle = 0.62f;
constexpr float kFirstTarget = 1.0f;
constexpr float kHardTarget = 9.0f;   // понад повноваження апарата (~6.7 м/с)
constexpr float kCalmTarget = 0.0f;

/*
 * Конфігурація контуру вертикальної швидкості. `constexpr` — отже,
 * лягає у Flash: одна копія на всі екземпляри регулятора.
 */
constexpr control::PidConfig kClimbConfig{
    .kp = 0.08f,
    .ki = 0.10f,
    .kd = 0.01f,
    .kff = 0.0667f,   // 1/15: стільки ходу газу коштує 1 м/с усталеної швидкості
    .out_min = 0.0f,
    .out_max = 1.0f,
    .i_min = 0.30f,   // вужче за межі виходу: лишаємо запас на P-маневр
    .i_max = 0.85f,
    .slew_rate_max = 2.0f
};

std::string flags_text(control::PidFlag flags)
{
    using control::PidFlag;
    struct Entry {
        PidFlag bit;
        std::string_view name;
    };
    constexpr std::array<Entry, 6> table{{
        {PidFlag::Saturated, "SAT"},
        {PidFlag::IntegralClamped, "ICLAMP"},
        {PidFlag::IntegralHeld, "IHOLD"},
        {PidFlag::SensorFault, "NAN"},
        {PidFlag::InvalidDt, "DT"},
        {PidFlag::Slewing, "SLEW"},
    }};

    std::string out;
    for (const auto& [bit, name] : table) {
        if (!control::holds(flags, bit)) {
            continue;
        }
        if (!out.empty()) {
            out.push_back('|');
        }
        out.append(name);
    }
    return out.empty() ? std::string{"-"} : out;
}

void print_header()
{
    std::cout << "   t,с  режим   v_вим  v_уст      u       P      I       D      FF  прапорці\n"
                 "  --------------------------------------------------------------------------\n";
}

void print_row(float t, std::string_view mode, float measurement,
               const control::PidTelemetry& tr, float output)
{
    std::cout << std::format(
        "  {:5.2f}  {:<6} {:6.3f} {:6.3f}  {:6.3f}  {:6.3f} {:6.3f}  {:6.3f}  {:6.3f}  {}\n",
        t, mode, measurement, tr.setpoint, output,
        tr.p_term, tr.i_term, tr.d_term, tr.ff_term, flags_text(tr.flags));
}

/*
 * Що видав би на перемиканні регулятор, який просто почав з чистого стану:
 * інтеграл нуль, історія виміру взята з давача. Уставка на цей момент
 * дорівнює виміру, тож лишається самий прямий зв'язок.
 */
[[nodiscard]] float naive_first_output(float measurement) noexcept
{
    return control::num::clamp_to(kClimbConfig.kff * measurement,
                                  kClimbConfig.out_min, kClimbConfig.out_max);
}

} // namespace

int main()
{
    demo::ClimbRatePlant plant{0.55f};
    control::BumplessPidController pid{kClimbConfig};
    control::PidTelemetry trace{};

    if (!pid.is_initialized()) {
        std::cout << "Конфігурація контуру непридатна — регулятор не запущено.\n";
        return 1;
    }

    std::cout << "Безривкова передача повноважень: контур вертикальної швидкості\n";
    std::cout << std::format("Такт {:.0f} Гц, завислість {:.2f}, ручний хід газу {:.2f}\n\n",
                             1.0f / kDt, plant.hover_throttle(), kManualThrottle);
    print_header();

    float t = 0.0f;
    float u = kManualThrottle;
    float next_print = 0.0f;
    bool auto_mode = false;
    bool demanded = false;
    bool relaxed = false;
    bool switch_captured = false;
    float u_before_switch = 0.0f;
    float u_after_switch = 0.0f;
    float m_at_switch = 0.0f;

    while (t < kEndAt) {
        const bool fault = (t >= kFaultFrom && t < kFaultTo);
        const float measurement = plant.sample(fault);
        std::string_view mode = "РУЧН";

        if (!auto_mode && t >= kSwitchAt) {
            /*
             * Той самий свіжий відлік іде і в передачу, і в перший update
             * цього ж такту — саме за цієї умови вимога
             * |u(0+) − prev_actuator_output| == 0 виконується бітово.
             */
            pid.handover(measurement, kFirstTarget, u);
            u_before_switch = u;
            m_at_switch = measurement;
            auto_mode = true;
        }

        if (auto_mode && !demanded && t >= kDemandAt) {
            pid.set_target(kHardTarget);
            demanded = true;
        }
        if (auto_mode && !relaxed && t >= kRelaxAt) {
            pid.set_target(kCalmTarget);
            relaxed = true;
        }

        if (auto_mode) {
            mode = "АВТО";
            u = pid.update(measurement, kDt, trace);
            if (!switch_captured) {
                // Перший такт під керуванням регулятора — той самий, у якому
                // відбулася передача. Саме його порівнюємо з ручним ходом.
                u_after_switch = u;
                switch_captured = true;
            }
        } else {
            // У ручному режимі регулятор мовчить, але стан тримає.
            u = kManualThrottle;
            trace = control::PidTelemetry{};
        }

        plant.step(u, kDt);

        if (t + 0.5f * kDt >= next_print) {
            print_row(t, mode, measurement, trace, u);
            next_print += kPrintPeriod;
        }
        t += kDt;
    }

    const float bumpless_jump = std::fabs(u_after_switch - u_before_switch);
    const float naive_jump = std::fabs(u_before_switch - naive_first_output(m_at_switch));

    std::cout << std::format("\nСтик на перемиканні (t = {:.2f} с, вимір {:.3f} м/с):\n",
                             kSwitchAt, m_at_switch);
    std::cout << std::format("  безривкова передача : |{:.6f} − {:.6f}| = {:.6f}\n",
                             u_after_switch, u_before_switch, bumpless_jump);
    std::cout << std::format("  наївний рестарт     : |{:.6f} − {:.6f}| = {:.6f}  ← удар по моторах\n",
                             naive_first_output(m_at_switch), u_before_switch, naive_jump);
    std::cout << std::format("\nВідкинутих тактів через нескінченний вимір: {}\n",
                             pid.fault_count());
    std::cout << std::format("Висота наприкінці: {:.2f} м, швидкість {:.3f} м/с\n",
                             plant.altitude(), plant.climb_rate());
    return 0;
}
