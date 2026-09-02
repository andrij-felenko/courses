#include "bumpless/hil.hpp"

#include "bumpless/pid.hpp"
#include "bumpless/plant.hpp"

#include <algorithm>
#include <array>
#include <cmath>

namespace bumpless {
namespace {

constexpr float kDt = 0.0025f;

// Бібліотека режимів для тесту нульового стрибка: різні коефіцієнти, різний
// прогнозний внесок, однакові межі приводу — щоб трим переходив із рук у руки.
constexpr std::array<PidConfig, 4> kModeLibrary{{
    {.kp = 0.60f, .ki = 0.90f, .kd = 0.05f, .kff = 0.00f,
     .out_min = -1.0f, .out_max = 1.0f, .i_min = -0.95f, .i_max = 0.95f,
     .slew_rate_max = 30.0f, .d_lpf_tau = 0.02f, .max_expected_noise = 0.02f},
    {.kp = 0.18f, .ki = 0.25f, .kd = 0.30f, .kff = 0.15f,
     .out_min = -1.0f, .out_max = 1.0f, .i_min = -0.95f, .i_max = 0.95f,
     .slew_rate_max = 5.0f, .d_lpf_tau = 0.05f, .max_expected_noise = 0.03f},
    {.kp = 1.20f, .ki = 0.05f, .kd = 0.00f, .kff = 0.00f,
     .out_min = -1.0f, .out_max = 1.0f, .i_min = -0.95f, .i_max = 0.95f,
     .slew_rate_max = 0.0f, .d_lpf_tau = 0.00f, .max_expected_noise = 0.01f},
    {.kp = 0.35f, .ki = 1.40f, .kd = 0.12f, .kff = 0.40f,
     .out_min = -1.0f, .out_max = 1.0f, .i_min = -0.95f, .i_max = 0.95f,
     .slew_rate_max = 2.5f, .d_lpf_tau = 0.03f, .max_expected_noise = 0.05f},
}};

constexpr PidConfig kAltitudeHold{
    .kp = 0.10f, .ki = 0.06f, .kd = 0.15f, .kff = 0.0f,
    .out_min = 0.0f, .out_max = 1.0f, .i_min = 0.0f, .i_max = 0.95f,
    .slew_rate_max = 2.5f, .d_lpf_tau = 0.05f, .max_expected_noise = 0.05f};

// 1. Тест нульового стрибка: 50 перемикань між усіма режимами по колу.
//    Вимір навмисно тримаємо сталим — тест судить алгоритм, а не фізику:
//    якби апарат між тактами рухався, P і D дали б цілком законний внесок.
void run_glitch_test(HilReport& rep)
{
    constexpr float measurement = 0.30f; // збурений стаціонар: вітер вимагає триму
    float u_prev = 0.30f;

    rep.switch_count = 50u;
    rep.glitch_limit = 1e-4f;
    rep.glitch_worst = 0.0f;

    for (unsigned i = 0; i < rep.switch_count; ++i) {
        BumplessPidController pid{kModeLibrary[i % kModeLibrary.size()]};
        pid.handover(measurement, measurement, u_prev);

        const float u = pid.update(measurement, kDt);
        rep.glitch_worst = std::max(rep.glitch_worst, std::abs(u - u_prev));

        // Наступний режим приймає повноваження вже з рук цього.
        u_prev = u;
    }

    rep.glitch_pass = rep.glitch_worst < rep.glitch_limit;
}

// 2. Тест насиченого передзавантаження: привід стоїть на упорі 100 %,
//    апарат розігнаний угору, вмикається утримання висоти.
void run_saturated_test(HilReport& rep)
{
    QuadPlant plant{1.8f, 0.52f, 60.0f};
    for (int i = 0; i < 400; ++i) { // 1 с повного газу — вертикальний розгін
        plant.step(1.0f, kDt);
    }

    BumplessPidController pid{kAltitudeHold};
    pid.handover(plant.altitude(), plant.altitude(), 1.0f);

    const auto limits = kAltitudeHold.safe_integral_limits();
    const float preloaded = pid.integral();
    const float u_start = pid.last_output();
    rep.saturated_residual = std::abs(1.0f - u_start);

    float min_integral = preloaded;
    float u_after_10 = u_start;

    const int steps = static_cast<int>(3.0f / kDt);
    for (int i = 0; i < steps; ++i) {
        const float u = pid.update(plant.altitude(), kDt);
        if (i == 9) {
            u_after_10 = u;
        }
        min_integral = std::min(min_integral, pid.integral());
        plant.step(u, kDt);
    }

    rep.saturated_first_delta = u_after_10 - u_start;
    rep.saturated_integral_drop = preloaded - min_integral;

    // Залишковий стрибок не може бути меншим за резерв, який ми свідомо
    // лишили пропорційній ланці, — але й більшим ставати не має права.
    const float irreducible = kAltitudeHold.out_max - limits.hi;
    rep.saturated_pass = rep.saturated_residual <= irreducible + 1e-4f
                         && contains(pid.faults(), Fault::PreloadClamped)
                         && rep.saturated_first_delta < 0.0f
                         && rep.saturated_integral_drop > 0.01f;
}

// 3. Тест темпу наростання: після захоплення місія просить +200 м.
void run_ramping_test(HilReport& rep)
{
    constexpr float hover = 0.52f;

    QuadPlant plant{1.8f, hover, 25.0f};
    for (int i = 0; i < 400; ++i) {
        plant.step(hover, kDt);
    }

    BumplessPidController pid{kAltitudeHold};
    pid.handover(plant.altitude(), plant.altitude() + 200.0f, hover);

    rep.ramp_allowed_setpoint_step = kAltitudeHold.slew_rate_max * kDt;

    float prev_sp = pid.current_setpoint();
    unsigned saturated_run = 0u;

    const int steps = static_cast<int>(100.0f / kDt);
    for (int i = 0; i < steps; ++i) {
        const float u = pid.update(plant.altitude(), kDt);

        const float sp = pid.current_setpoint();
        rep.ramp_peak_setpoint_step = std::max(rep.ramp_peak_setpoint_step,
                                               std::abs(sp - prev_sp));
        prev_sp = sp;

        if (u >= kAltitudeHold.out_max - 1e-6f) {
            ++saturated_run;
            rep.ramp_max_saturated_run = std::max(rep.ramp_max_saturated_run, saturated_run);
        } else {
            saturated_run = 0u;
        }

        plant.step(u, kDt);

        const float n = plant.load_factor();
        rep.ramp_peak_load_g = std::max(rep.ramp_peak_load_g, n);
        rep.ramp_min_load_g = std::min(rep.ramp_min_load_g, n);
    }

    // Пік струму моторів прямо не міряємо — його заступником є найдовша
    // серія тактів на упорі газу: саме там мотор тягне пусковий струм.
    rep.ramp_pass = rep.ramp_peak_setpoint_step <= rep.ramp_allowed_setpoint_step * 1.001f
                    && rep.ramp_peak_load_g <= 2.5f
                    && rep.ramp_min_load_g >= -0.5f
                    && rep.ramp_max_saturated_run < static_cast<unsigned>(0.5f / kDt);
}

} // namespace

HilReport run_hil_suite()
{
    HilReport rep{};
    run_glitch_test(rep);
    run_saturated_test(rep);
    run_ramping_test(rep);
    return rep;
}

} // namespace bumpless
