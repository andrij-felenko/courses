#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <string_view>

#include "authority.hpp"
#include "nav_loop.hpp"
#include "rc_link.hpp"
#include "telemetry.hpp"
#include "types.hpp"

// Прогін сценарію зі статті: літак іде за маршрутом на 22 м/с і 45 м, збоку
// дме вітер, на 2-й секунді пілот смикає стік на себе і вправо, обходячи трос
// крана, а потім відпускає ручку. Модель планера навмисно проста — вона
// потрібна лише для того, щоб побачити роботу перехоплення.

namespace {

using namespace fc;

constexpr Seconds kDt{0.005f}; // 200 Гц
constexpr float kRunSec = 9.0f;
constexpr float kWindY = 6.0f; // м/с, вітер зліва зносить апарат по +y
constexpr float kPilotRollLimitDeg = 45.0f;
constexpr float kPilotPitchLimitDeg = 15.0f;
constexpr float kPilotYawLimitDps = 20.0f;
constexpr float kManeuverEndSec = 3.6f;

struct Plane {
    VehicleState st{0.0f, 0.0f, 45.0f, 0.0f, 22.0f};
    float roll_deg{0.0f};  // приводи й планер відстають від команди
    float pitch_deg{0.0f};

    void step(const ControlCommand& u, Seconds dt_s) noexcept {
        const float dt = dt_s.count();
        roll_deg += (u.roll - roll_deg) * (dt / (0.25f + dt));
        pitch_deg += (u.pitch - pitch_deg) * (dt / (0.40f + dt));

        const float roll_rad = roll_deg * kDeg2Rad;
        const float pitch_rad = pitch_deg * kDeg2Rad;

        // Координований розворот: правий крен веде ніс за годинниковою
        // стрілкою, тобто курс у нашій системі координат спадає.
        const float turn_rate = (9.81f / std::max(st.airspeed, 8.0f)) *
                                std::tan(roll_rad) * kRad2Deg;
        st.heading_deg = wrap180(st.heading_deg - turn_rate * dt);

        const float hdg = st.heading_deg * kDeg2Rad;
        st.x += st.airspeed * std::cos(hdg) * dt;
        st.y += (st.airspeed * std::sin(hdg) + kWindY) * dt;
        st.alt += st.airspeed * std::sin(pitch_rad) * dt;

        const float spd_eq = 12.0f + 15.0f * u.throttle - 20.0f * std::sin(pitch_rad);
        st.airspeed += (spd_eq - st.airspeed) * (dt / (1.5f + dt));
        st.airspeed = std::max(st.airspeed, 8.0f);
    }
};

struct StickPosition {
    float roll{0.0f};
    float pitch{0.0f};
    float throttle{0.30f}; // важіль лишається там, де його поклали
    FlightMode mode{FlightMode::Auto};
};

// Що робить пілот. Важіль газу весь політ не рухається: це і є неузгодженість
// газу з пастки номер два.
StickPosition pilot_script(float t) noexcept {
    StickPosition s;
    if (t >= 2.0f && t < kManeuverEndSec) {
        s.roll = 0.75f;  // правий крен
        s.pitch = 0.90f; // стік на себе — набір висоти
    }
    return s;
}

constexpr std::uint16_t to_pwm_sym(float v) noexcept {
    return static_cast<std::uint16_t>(1500.0f + 500.0f * std::clamp(v, -1.0f, 1.0f) + 0.5f);
}

constexpr std::uint16_t to_pwm_uni(float v) noexcept {
    return static_cast<std::uint16_t>(1000.0f + 1000.0f * std::clamp(v, 0.0f, 1.0f) + 0.5f);
}

constexpr std::uint16_t mode_pwm(FlightMode m) noexcept {
    switch (m) {
        case FlightMode::Auto: return 1100;
        case FlightMode::PosHold: return 1500;
        case FlightMode::Manual: return 1900;
    }
    return 1500;
}

struct Scenario {
    std::string_view title;
    bool anti_windup{true};
    float rc_loss_at{-1.0f}; // с; від'ємне — зв'язок не втрачається
    float fence_at{-1.0f};   // с; від'ємне — геозону не порушуємо
};

void run(const Scenario& sc) {
    Plane plane;
    NavLoop nav{NavLoop::Setpoint{0.0f, 0.0f, 3000.0f, 0.0f, 45.0f, 22.0f}};
    nav.set_anti_windup(sc.anti_windup);

    RcLink link;
    AuthorityManager authority;
    Telemetry telemetry;

    ControlCommand prev_out{};
    ControlCommand prev_mux{};
    bool have_prev = false;

    float max_rate_blend = 0.0f; // °/с на виході змішувача
    float max_rate_mux = 0.0f;   // °/с, якби стояв простий мультиплексор
    float max_abs_i = 0.0f;
    float max_xte_after = 0.0f;
    float next_print = 0.0f;

    std::printf("\n=== %.*s ===\n", static_cast<int>(sc.title.size()), sc.title.data());
    std::printf("   t    стан           alpha  thr    xte      I     roll    alt   thr\n");

    const int steps = static_cast<int>(kRunSec / kDt.count());
    for (int i = 0; i <= steps; ++i) {
        const Seconds now{static_cast<float>(i) * kDt.count()};
        const float t = now.count();

        const StickPosition sticks = pilot_script(t);
        if (sc.rc_loss_at < 0.0f || t < sc.rc_loss_at) {
            const std::array<std::uint16_t, RcLink::kChannels> frame{
                to_pwm_sym(sticks.roll), to_pwm_sym(sticks.pitch),
                to_pwm_uni(sticks.throttle), to_pwm_sym(0.0f),
                mode_pwm(sticks.mode), 1500, 1500, 1500};
            static_cast<void>(link.push(frame, now));
        }

        const std::optional<RcCommand> rc = link.poll(now);
        const bool fence = (sc.fence_at >= 0.0f) && (t >= sc.fence_at);

        const Status st = authority.update(rc, fence, kDt);
        const ControlCommand u_auto = nav.step(plane.st, st.freeze_nav, kDt);

        ControlCommand u_pilot{};
        if (rc) {
            u_pilot = ControlCommand{rc->roll * kPilotRollLimitDeg,
                                     rc->pitch * kPilotPitchLimitDeg,
                                     rc->yaw * kPilotYawLimitDps, rc->throttle};
        }

        const ControlCommand u_out = blend(st.alpha, u_auto, u_pilot);

        // Той самий момент, але з наївним мультиплексором: жодного змішування,
        // перемикання за α > 0.5. Порівняння швидкостей — нижче в підсумку.
        const ControlCommand u_mux = (st.alpha.attitude > 0.5f) ? u_pilot : u_auto;

        if (have_prev) {
            max_rate_blend = std::max(max_rate_blend,
                                      std::abs(u_out.roll - prev_out.roll) / kDt.count());
            max_rate_mux = std::max(max_rate_mux,
                                    std::abs(u_mux.roll - prev_mux.roll) / kDt.count());
        }
        prev_out = u_out;
        prev_mux = u_mux;
        have_prev = true;

        max_abs_i = std::max(max_abs_i, std::abs(nav.integral()));

        plane.step(u_out, kDt);

        if (t >= kManeuverEndSec) {
            max_xte_after = std::max(max_xte_after, std::abs(nav.crosstrack(plane.st)));
        }

        telemetry.report(authority.events(), now);
        telemetry.stream(st, now);

        if (t + 1e-4f >= next_print) {
            next_print += 0.25f;
            const std::string_view name = to_string(st.phase);
            std::printf("%5.2f  %-13.*s %.2f  %.2f %+7.1f %+6.1f %+7.1f %6.1f  %.2f\n",
                        static_cast<double>(t), static_cast<int>(name.size()), name.data(),
                        static_cast<double>(st.alpha.attitude),
                        static_cast<double>(st.alpha.throttle),
                        static_cast<double>(nav.crosstrack(plane.st)),
                        static_cast<double>(nav.integral()),
                        static_cast<double>(u_out.roll),
                        static_cast<double>(plane.st.alt),
                        static_cast<double>(u_out.throttle));
        }
    }

    std::printf("  підсумок: |I|max=%.1f°  найбільший відхід після віддачі=%.1f м\n",
                static_cast<double>(max_abs_i), static_cast<double>(max_xte_after));
    std::printf("  швидкість зміни команди крену: змішувач %.0f °/с, "
                "наївний мультиплексор %.0f °/с\n",
                static_cast<double>(max_rate_blend), static_cast<double>(max_rate_mux));
}

} // namespace

int main() {
    constexpr std::array<Scenario, 4> scenarios{
        Scenario{"Обхід троса: захисти увімкнено", true, -1.0f, -1.0f},
        Scenario{"Те саме без анти-віндапу й синхронізації уставки", false, -1.0f, -1.0f},
        Scenario{"Втрата RC посеред ручного маневру", true, 2.8f, -1.0f},
        Scenario{"Геозона забирає керування в пілота", true, -1.0f, 2.8f}};

    for (const Scenario& sc : scenarios) run(sc);
    return 0;
}
