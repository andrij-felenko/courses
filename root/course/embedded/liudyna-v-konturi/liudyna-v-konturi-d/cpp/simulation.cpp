#include "simulation.hpp"

#include <algorithm>
#include <cmath>
#include <format>
#include <ostream>

#include "link.hpp"
#include "pilot.hpp"
#include "pio.hpp"

namespace hitl {
namespace {

constexpr float kDt = 0.002f;       // 500 Гц — крок дискретизації
constexpr float kSimSeconds = 8.0f;
constexpr float kRadToDeg = 57.2957795f;
constexpr float kOmegaCrossover = 2.5f;  // робоча частота зрізу людини, рад/с

// Порив вітру: імпульс моменту 0.8 Н*м тривалістю 150 мс на 0.5 с.
float Gust(float t) noexcept { return (t >= 0.5f && t < 0.65f) ? 0.8f : 0.0f; }

}  // namespace

Report Run(const Scenario& sc, std::ostream& trace) {
    Airframe air{0.02f, 0.05f, 1.2f};
    Autopilot autopilot{sc.mode, kDt};
    autopilot.EnableSuppression(sc.pio_suppression);

    // Відеотракт забирає ~70% лагу, командний радіолінк ~30%.
    DelayLine<Telemetry> video{sc.link_delay * 0.7f, sc.jitter, sc.jitter_buffer,
                               0xBEEFu};
    DelayLine<float> uplink{sc.link_delay * 0.3f, 0.0f, false, 0xF00Du};

    const ObjectDynamics object = autopilot.Describe(air);
    const PilotParams params = TuneByCrossoverLaw(object, kOmegaCrossover);
    Pilot pilot{params, kDt};

    Report r;
    r.pilot_gain = params.kp;
    r.pilot_lead = params.lead_tc;
    r.pure_delay = params.reaction_delay + video.effective_delay() +
                   uplink.effective_delay();
    r.phase_margin0_deg = PhaseMarginWithoutDelay(params, object, kOmegaCrossover);
    r.phase_margin_deg =
        PhaseMargin(r.phase_margin0_deg, kOmegaCrossover, r.pure_delay);
    r.link_budget = std::max(0.0f, CriticalDelay(r.phase_margin0_deg, kOmegaCrossover) -
                                       params.reaction_delay);

    PioMonitor angle_monitor{kDt};
    PioMonitor rate_monitor{kDt};
    PioMonitor stick_monitor{kDt};
    PioCorrelator correlator{kDt, 1.5f};

    const int steps = static_cast<int>(kSimSeconds / kDt);
    for (int i = 0; i < steps; ++i) {
        const float t = static_cast<float>(i) * kDt;

        // 1. Борт віддає телеметрію у відеотракт.
        video.Push(Telemetry{air.angle(), air.rate()}, t);
        const Telemetry seen = video.Pop(t);

        // 2. Наземна станція за потреби малює прогнозну позначку
        //    y_pred = y + tau*v — це компенсує фазовий набіг затримки.
        const float shown =
            sc.lead_ahead_hud ? seen.angle_rad + r.pure_delay * seen.rate_rad_s
                              : seen.angle_rad;

        // 3. Оператор бачить похибку: уставка — горизонт, r = 0.
        const float stick = pilot.Update(0.0f - shown, t, kDt);

        // 4. Крива пульта й політ команди зворотним радіоканалом.
        uplink.Push(RcExpo(stick, sc.expo), t);
        const float onboard_stick = uplink.Pop(t);

        // 5. Бортовий контролер і фізика апарата.
        const float torque = autopilot.Update(onboard_stick, air, kDt);
        air.Step(torque, Gust(t), kDt);

        // 6. Діагностика — рівно те, що інженер робить із логом польоту.
        angle_monitor.Update(air.angle());
        rate_monitor.Update(air.rate());
        stick_monitor.Update(stick);
        correlator.Update(stick_monitor.oscillation(), rate_monitor.oscillation());

        r.max_angle_deg =
            std::max(r.max_angle_deg, std::abs(air.angle()) * kRadToDeg);
        if (i % 500 == 0) {
            trace << std::format(
                "    t={:4.1f} c | кут {:7.1f} град | стік {:6.2f} | "
                "переляк {:.2f} | чутливість {:.2f}\n",
                t, air.angle() * kRadToDeg, stick, pilot.panic(),
                autopilot.sensitivity());
        }
    }

    r.osc_freq_hz = angle_monitor.frequency_hz();
    r.osc_amp_deg = angle_monitor.amplitude() * kRadToDeg;
    r.osc_growth = angle_monitor.growth();
    r.stick_gyro_corr = correlator.value();
    r.saturation = autopilot.saturation_ratio();
    r.video_freezes = video.freezes();
    // Підпис PIO: коливання в людській смузі, помітна амплітуда й стік у
    // протифазі до гіроскопа. Вібрація рами чи D-терм так не виглядають.
    r.pio = angle_monitor.IsPio(0.10f) && r.stick_gyro_corr < -0.3f;
    return r;
}

}  // namespace hitl
