#include "bumpless/cascade.hpp"
#include "bumpless/hil.hpp"
#include "bumpless/irq_guard.hpp"
#include "bumpless/pid.hpp"
#include "bumpless/plant.hpp"
#include "bumpless/ramp.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <format>
#include <iostream>
#include <numbers>
#include <string_view>
#include <utility>

namespace {

using namespace bumpless;

constexpr float kDtFast = 0.001f;  // внутрішній контур кута — 1 кГц
constexpr float kDtLoop = 0.0025f; // контур висоти — 2.5 мс, як у прикладі зі статті

constexpr PidConfig kAltitudeHold{
    .kp = 0.10f,  // частка газу на метр помилки
    .ki = 0.06f,
    .kd = 0.15f,  // демпфування за вертикальною швидкістю
    .kff = 0.0f,
    .out_min = 0.0f, .out_max = 1.0f,
    .i_min = 0.0f, .i_max = 0.95f,
    .slew_rate_max = 2.5f, // м/с — паспортна швидкість набору
    .d_lpf_tau = 0.05f,
    .max_expected_noise = 0.05f};

constexpr float to_degrees(float radians) noexcept
{
    return radians * 180.0f / std::numbers::pi_v<float>;
}

// ------------------------------------------------------------------
// 1. Наївний перезапуск проти безривкового переходу
// ------------------------------------------------------------------

struct HoldStats {
    float first_output{0.0f};
    float first_jump{0.0f};
    float min_altitude{0.0f};
    float max_altitude{0.0f};
    float min_load_g{1.0f};
    float settle_seconds{0.0f};
};

HoldStats run_altitude_hold(bool bumpless_start, float seconds)
{
    constexpr float hover = 0.52f;

    QuadPlant plant{1.8f, hover, 25.0f};
    for (int i = 0; i < 400; ++i) { // усталений висячий політ під ручним газом
        plant.step(hover, kDtLoop);
    }

    BumplessPidController pid{kAltitudeHold};
    const float h0 = plant.altitude();
    if (bumpless_start) {
        pid.handover(h0, h0, hover);
    } else {
        // Той самий «чистий аркуш»: уставка з місії, інтегратор нуль,
        // пам'ять диференціатора порожня.
        pid.start_naive(h0);
    }

    HoldStats st{};
    st.min_altitude = h0;
    st.max_altitude = h0;

    const int steps = static_cast<int>(seconds / kDtLoop);
    for (int i = 0; i < steps; ++i) {
        const float u = pid.update(plant.altitude(), kDtLoop);
        if (i == 0) {
            st.first_output = u;
            st.first_jump = std::abs(u - hover);
        }

        plant.step(u, kDtLoop);

        st.min_altitude = std::min(st.min_altitude, plant.altitude());
        st.max_altitude = std::max(st.max_altitude, plant.altitude());
        st.min_load_g = std::min(st.min_load_g, plant.load_factor());

        // Заспокоєнням вважаємо мить, після якої апарат уже не виходить
        // за чверть метра від точки, в якій його застало перемикання.
        if (std::abs(plant.altitude() - h0) > 0.25f) {
            st.settle_seconds = static_cast<float>(i + 1) * kDtLoop;
        }
    }
    return st;
}

// ------------------------------------------------------------------
// 2. Три генератори траєкторії
// ------------------------------------------------------------------

enum class RampMethod { Slew, Lpf, SCurve };

struct RampStats {
    float peak_climb_mps{0.0f};
    float peak_load_g{1.0f};
    float time_to_target_s{0.0f};
    float overshoot_m{0.0f};
};

RampStats run_ramp(RampMethod method, float climb_m, float seconds)
{
    constexpr float hover = 0.52f;

    QuadPlant plant{1.8f, hover, 25.0f};
    for (int i = 0; i < 400; ++i) {
        plant.step(hover, kDtLoop);
    }

    PidConfig cfg = kAltitudeHold;
    if (method != RampMethod::Slew) {
        // Уставку формує зовнішній генератор — власний ремпінг контуру
        // вимикаємо, інакше два обмежувачі різатимуть той самий сигнал.
        cfg.slew_rate_max = 0.0f;
    }

    const float h0 = plant.altitude();
    const float goal = h0 + climb_m;

    BumplessPidController pid{cfg};
    pid.handover(h0, (method == RampMethod::Slew) ? goal : h0, hover);

    float shaped = h0;
    SCurve curve{h0, goal, 2.5f, 1.5f, 2.0f};

    RampStats st{};
    st.time_to_target_s = seconds;
    bool reached = false;

    const int steps = static_cast<int>(seconds / kDtLoop);
    for (int i = 0; i < steps; ++i) {
        switch (method) {
        case RampMethod::Lpf:
            shaped = lpf_step(shaped, goal, kDtLoop, 1.5f);
            pid.set_target(shaped);
            break;
        case RampMethod::SCurve:
            curve.step(kDtLoop);
            pid.set_target(curve.position());
            break;
        case RampMethod::Slew:
            break; // ремпінг живе всередині самого контуру
        }

        const float u = pid.update(plant.altitude(), kDtLoop);
        plant.step(u, kDtLoop);

        st.peak_climb_mps = std::max(st.peak_climb_mps, std::abs(plant.vertical_speed()));

        const float n = plant.load_factor();
        if (std::abs(n - 1.0f) > std::abs(st.peak_load_g - 1.0f)) {
            st.peak_load_g = n;
        }

        if (!reached && std::abs(plant.altitude() - goal) < 0.30f) {
            reached = true;
            st.time_to_target_s = static_cast<float>(i + 1) * kDtLoop;
        }
        st.overshoot_m = std::max(st.overshoot_m, plant.altitude() - goal);
    }
    return st;
}

// ------------------------------------------------------------------
// 3. Каскад: наївний, розірваний і атомарний перехід
// ------------------------------------------------------------------

enum class HandoverKind { Naive, Torn, Atomic };

struct CascadeStats {
    float first_jump{0.0f};
    float worst_jump{0.0f};
    float max_drift_m{0.0f};
    float max_angle_deg{0.0f};
};

// Попередній режим: пілот тримає апарат простим ПД по куту. Інтегратора в
// нього немає, тож позицію він тримає з невеликим статичним зсувом — зате
// саме він напрацював ту команду приводу, яку каскад мусить успадкувати.
float manual_hold(const LateralPlant& plant) noexcept
{
    const float angle_cmd = std::clamp(-0.35f * plant.position() - 0.55f * plant.velocity(),
                                       -0.40f, 0.40f);
    return std::clamp(6.0f * (angle_cmd - plant.angle()), -1.0f, 1.0f);
}

CascadeConfig position_hold_config()
{
    CascadeConfig cfg{};

    // Контур позиції (20 Гц). Інтегратора не має навмисно: сталий трим
    // тримає нижній поверх, дублювати його зверху немає потреби.
    cfg.position = PidConfig{.kp = 0.50f, .ki = 0.0f, .kd = 0.0f, .kff = 0.0f,
                             .out_min = -3.0f, .out_max = 3.0f,
                             .i_min = -1.0f, .i_max = 1.0f,
                             .slew_rate_max = 1.0f, .d_lpf_tau = 0.0f,
                             .max_expected_noise = 0.05f};

    // Контур швидкості (50 Гц): його вихід — уставка кута в радіанах.
    cfg.velocity = PidConfig{.kp = 0.12f, .ki = 0.05f, .kd = 0.0f, .kff = 0.0f,
                             .out_min = -0.35f, .out_max = 0.35f,
                             .i_min = -0.35f, .i_max = 0.35f,
                             .slew_rate_max = 0.0f, .d_lpf_tau = 0.0f,
                             .max_expected_noise = 0.05f};

    // Контур кута (1 кГц): його вихід — нормалізована команда на мотори.
    cfg.angle = PidConfig{.kp = 6.00f, .ki = 2.00f, .kd = 0.0f, .kff = 0.0f,
                          .out_min = -1.0f, .out_max = 1.0f,
                          .i_min = -1.0f, .i_max = 1.0f,
                          .slew_rate_max = 0.0f, .d_lpf_tau = 0.0f,
                          .max_expected_noise = 0.01f};

    cfg.velocity_from_position_gain = 1.0f;
    cfg.angle_from_velocity_gain = 1.0f;
    cfg.position_divider = 50u; // 1 кГц / 50 = 20 Гц
    cfg.velocity_divider = 20u; // 1 кГц / 20 = 50 Гц
    return cfg;
}

CascadeStats run_cascade(HandoverKind kind, float seconds)
{
    LateralPlant plant{LateralParams{}};

    float u_manual = 0.0f;
    for (int i = 0; i < static_cast<int>(12.0f / kDtFast); ++i) {
        u_manual = manual_hold(plant);
        plant.step(u_manual, kDtFast);
    }

    CascadeController cascade{position_hold_config()};
    CascadeMeasurement m = measure(plant);
    constexpr float target_position = 0.0f;
    constexpr unsigned tear_ticks = 20u; // 20 мс між половинами транзакції

    switch (kind) {
    case HandoverKind::Naive:
        cascade.start_naive(target_position);
        break;
    case HandoverKind::Torn:
        // Перемикання почалося в задачі 20 Гц і не встигло дійти до верхніх
        // поверхів: швидкий контур уже працює, зовнішні ще ні.
        cascade.load_inner(m, u_manual);
        break;
    case HandoverKind::Atomic:
        cascade.handover(m, target_position, u_manual);
        break;
    }

    CascadeStats st{};
    st.max_drift_m = std::abs(plant.position());
    st.max_angle_deg = std::abs(to_degrees(plant.angle()));

    const int steps = static_cast<int>(seconds / kDtFast);
    for (int i = 0; i < steps; ++i) {
        if (kind == HandoverKind::Torn && static_cast<unsigned>(i) == tear_ticks) {
            cascade.load_outer(measure(plant), target_position);
        }

        if (IrqGuard::locked()) {
            // Транзакція перемикання ще триває — швидкий контур чесно
            // відкладає свій такт, а не рахує на напівзавантаженому стані.
            IrqGuard::note_deferred_tick();
            continue;
        }

        m = measure(plant);
        const float u = cascade.update(m, kDtFast);

        const float jump = std::abs(u - u_manual);
        if (i == 0) {
            st.first_jump = jump;
        }
        if (static_cast<unsigned>(i) <= tear_ticks) {
            st.worst_jump = std::max(st.worst_jump, jump);
        }

        plant.step(u, kDtFast);

        st.max_drift_m = std::max(st.max_drift_m, std::abs(plant.position()));
        st.max_angle_deg = std::max(st.max_angle_deg, std::abs(to_degrees(plant.angle())));
    }
    return st;
}

// ------------------------------------------------------------------
// 4. Команда проти телеметрії вала
// ------------------------------------------------------------------

struct ServoStats {
    float shaft_at_switch_deg{0.0f};
    float first_command_deg{0.0f};
    float extra_travel_deg{0.0f};
};

ServoStats run_servo_handover(bool use_telemetry)
{
    Servo servo{400.0f, 0.3f, 0.0f}; // 0.15 с на 60 градусів

    constexpr float pilot_command = 25.0f;
    for (int i = 0; i < 8; ++i) { // 20 мс різкого маневру: вал відстає
        servo.step(pilot_command, kDtLoop);
    }

    const float shaft = servo.position();

    constexpr PidConfig cfg{.kp = 0.80f, .ki = 1.20f, .kd = 0.0f, .kff = 0.0f,
                            .out_min = -30.0f, .out_max = 30.0f,
                            .i_min = -30.0f, .i_max = 30.0f,
                            .slew_rate_max = 0.0f, .d_lpf_tau = 0.0f,
                            .max_expected_noise = 0.2f};

    BumplessPidController pid{cfg};

    // Ось і вся різниця: чим саме ми вважаємо u_prev.
    const float u_prev = use_telemetry ? shaft : pilot_command;
    pid.handover(shaft, shaft, u_prev);

    ServoStats st{};
    st.shaft_at_switch_deg = shaft;

    const int steps = static_cast<int>(1.0f / kDtLoop);
    for (int i = 0; i < steps; ++i) {
        const float u = pid.update(servo.position(), kDtLoop);
        if (i == 0) {
            st.first_command_deg = u;
        }
        servo.step(u, kDtLoop);
        st.extra_travel_deg = std::max(st.extra_travel_deg,
                                       std::abs(servo.position() - shaft));
    }
    return st;
}

// ------------------------------------------------------------------

void print_hold_report()
{
    const HoldStats naive = run_altitude_hold(false, 15.0f);
    const HoldStats smooth = run_altitude_hold(true, 15.0f);

    std::cout << "1. Утримання висоти: перемикання на 25 м, газ висіння 0.52\n";
    std::cout << std::format("   {:<28} {:>12} {:>12}\n", "показник", "наївно", "безривково");
    std::cout << std::format("   {:<28} {:>12.4f} {:>12.4f}\n", "вихід на 1-му такті",
                             naive.first_output, smooth.first_output);
    std::cout << std::format("   {:<28} {:>12.4f} {:>12.4f}\n", "стрибок |du|",
                             naive.first_jump, smooth.first_jump);
    std::cout << std::format("   {:<28} {:>12.2f} {:>12.2f}\n", "просідання, м",
                             25.0f - naive.min_altitude, 25.0f - smooth.min_altitude);
    std::cout << std::format("   {:<28} {:>12.2f} {:>12.2f}\n", "переліт, м",
                             naive.max_altitude - 25.0f, smooth.max_altitude - 25.0f);
    std::cout << std::format("   {:<28} {:>12.2f} {:>12.2f}\n", "мінімальна перевантага, g",
                             naive.min_load_g, smooth.min_load_g);
    std::cout << std::format("   {:<28} {:>12.2f} {:>12.2f}\n\n", "заспокоєння, с",
                             naive.settle_seconds, smooth.settle_seconds);
}

void print_ramp_report()
{
    constexpr std::array<std::pair<RampMethod, std::string_view>, 3> methods{{
        {RampMethod::Slew, "обмежувач темпу"},
        {RampMethod::Lpf, "фільтр 1-го порядку"},
        {RampMethod::SCurve, "S-профіль"},
    }};

    std::cout << "2. Підведення до нової цілі: набір +15 м після захоплення\n";
    std::cout << std::format("   {:<22} {:>10} {:>10} {:>10} {:>10}\n",
                             "генератор", "пік м/с", "пік g", "час, с", "переліт");
    for (const auto& [method, name] : methods) {
        const RampStats st = run_ramp(method, 15.0f, 25.0f);
        std::cout << std::format("   {:<22} {:>10.2f} {:>10.3f} {:>10.2f} {:>10.2f}\n",
                                 name, st.peak_climb_mps, st.peak_load_g,
                                 st.time_to_target_s, st.overshoot_m);
    }
    std::cout << '\n';
}

void print_cascade_report()
{
    constexpr std::array<std::pair<HandoverKind, std::string_view>, 3> kinds{{
        {HandoverKind::Naive, "наївний"},
        {HandoverKind::Torn, "розірваний"},
        {HandoverKind::Atomic, "атомарний"},
    }};

    IrqGuard::reset_counters();
    std::cout << "3. Каскад позиція-швидкість-кут: захоплення позиції під боковим вітром\n";
    std::cout << std::format("   {:<14} {:>12} {:>12} {:>12} {:>12}\n",
                             "перехід", "|du| такт 1", "|du| пік", "знос, м", "крен, град");
    for (const auto& [kind, name] : kinds) {
        const CascadeStats st = run_cascade(kind, 12.0f);
        std::cout << std::format("   {:<14} {:>12.4f} {:>12.4f} {:>12.2f} {:>12.2f}\n",
                                 name, st.first_jump, st.worst_jump,
                                 st.max_drift_m, st.max_angle_deg);
    }
    std::cout << std::format("   критичних секцій: {}, відкладених швидких тактів: {}\n\n",
                             IrqGuard::lock_events(), IrqGuard::deferred_ticks());
}

void print_servo_report()
{
    const ServoStats commanded = run_servo_handover(false);
    const ServoStats telemetry = run_servo_handover(true);

    std::cout << "4. Передзавантаження командою проти телеметрії вала\n";
    std::cout << std::format("   вал у мить перемикання: {:.2f} град (команда пульта 25.00 град)\n",
                             commanded.shaft_at_switch_deg);
    std::cout << std::format("   {:<24} {:>14} {:>14}\n", "джерело u_prev",
                             "1-ша команда", "зайвий хід");
    std::cout << std::format("   {:<24} {:>14.2f} {:>14.2f}\n", "u_commanded",
                             commanded.first_command_deg, commanded.extra_travel_deg);
    std::cout << std::format("   {:<24} {:>14.2f} {:>14.2f}\n\n", "телеметрія вала",
                             telemetry.first_command_deg, telemetry.extra_travel_deg);
}

// Окремо показуємо, що робить регулятор із зіпсутим відліком давача.
void print_sensor_fault_report()
{
    BumplessPidController pid{kAltitudeHold};
    pid.handover(25.0f, 25.0f, 0.52f);

    const float good = pid.update(25.0f, kDtLoop);
    const float broken = pid.update(std::nanf(""), kDtLoop);
    const float stalled = pid.update(25.0f, 0.0f);

    std::cout << "5. Аномалії шини давача\n";
    std::cout << std::format("   справний відлік: {:.4f}, NaN: {:.4f}, dt = 0: {:.4f}\n",
                             good, broken, stalled);
    std::cout << std::format("   прапорці телеметрії: {}\n\n", describe(pid.faults()));
}

int print_hil_report()
{
    const HilReport rep = run_hil_suite();

    std::cout << "6. Чеклист HIL-стенда\n";
    std::cout << std::format("   [{}] нульовий стрибок: {} перемикань, найгірший |du| = {:.3e}"
                             " (межа {:.0e})\n",
                             rep.glitch_pass ? '+' : 'x', rep.switch_count,
                             rep.glitch_worst, rep.glitch_limit);
    std::cout << std::format("   [{}] насичене передзавантаження: залишок {:.4f},"
                             " вихід за 10 тактів {:.4f}, інтеграл зійшов на {:.4f}\n",
                             rep.saturated_pass ? '+' : 'x', rep.saturated_residual,
                             rep.saturated_first_delta, rep.saturated_integral_drop);
    std::cout << std::format("   [{}] темп наростання: крок уставки {:.5f} (дозволено {:.5f}),"
                             " перевантага {:.2f}..{:.2f} g, тактів на упорі {}\n",
                             rep.ramp_pass ? '+' : 'x', rep.ramp_peak_setpoint_step,
                             rep.ramp_allowed_setpoint_step, rep.ramp_min_load_g,
                             rep.ramp_peak_load_g, rep.ramp_max_saturated_run);

    if (!rep.all_passed()) {
        std::cout << "\n   ЧЕКЛИСТ НЕ ПРОЙДЕНО — у повітря не піднімаємо.\n";
        return 1;
    }
    std::cout << "\n   Чеклист пройдено.\n";
    return 0;
}

} // namespace

int main()
{
    std::cout << "Перехід без ривка: стан регулятора при зміні режиму\n\n";

    print_hold_report();
    print_ramp_report();
    print_cascade_report();
    print_servo_report();
    print_sensor_fault_report();
    return print_hil_report();
}
