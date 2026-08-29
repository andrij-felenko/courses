// Стенд диспетчера режимів.
// Збірка: c++ -std=c++23 -O2 -Iinclude src/*.cpp -o modes
// Три сценарії: перемикання режимів у польоті, підхоплення ручки і
// аварійний перехід при втраті зв'язку.

#include <chrono>
#include <cmath>
#include <format>
#include <iostream>

#include "altitude_fusion.hpp"
#include "crsf_link.hpp"
#include "mode_manager.hpp"

namespace {

using namespace std::chrono_literals;
using Millis = std::chrono::milliseconds;

constexpr float kDt = 0.02f;              // 50 Гц
constexpr float kHoverThrottle = 0.56f;

// Груба модель апарата: надлишок тяги над зависанням дає прискорення,
// опір повітря його з'їдає.
struct Plant {
    float altitude_m{0.0f};
    float climb_mps{0.0f};

    float step(float throttle, float dt) noexcept
    {
        const float acc = (throttle - kHoverThrottle) * 20.0f - 0.8f * climb_mps;
        climb_mps += acc * dt;
        altitude_m += climb_mps * dt;
        return acc;   // те, що побачить акселерометр
    }
};

std::uint16_t raw_from_unit(float unit) noexcept
{
    const float us = 988.0f + unit * 1024.0f;
    return static_cast<std::uint16_t>((us - 881.0f) / 0.62477f + 0.5f);
}

fc::crsf::Channels make_tx(float throttle, std::uint16_t aux1, bool override_on) noexcept
{
    fc::crsf::Channels tx{};
    tx.raw.fill(992);
    tx.raw[2] = raw_from_unit(throttle);          // газ
    tx.raw[4] = aux1;                             // AUX1 — режим
    tx.raw[5] = override_on ? 1792 : 191;         // AUX2 — силове перехоплення
    return tx;
}

fc::FlightMode mode_from_switch(fc::crsf::SwitchPos pos) noexcept
{
    switch (pos) {
    case fc::crsf::SwitchPos::Low: return fc::FlightMode::Manual;
    case fc::crsf::SwitchPos::Mid: return fc::FlightMode::AltHold;
    case fc::crsf::SwitchPos::High: return fc::FlightMode::AutoMission;
    }
    return fc::FlightMode::Manual;
}

// ── Сценарій 1: два перемикання в польоті ────────────────────────────────
void scenario_mode_switch()
{
    std::cout << "=== Сценарій 1: MANUAL -> ALT_HOLD -> AUTO_MISSION ===\n"
              << "Час[с] | Режим        | Висота[м] | Вихід    | Стрибок dU | Інтегратор\n"
              << "---------------------------------------------------------------------\n";

    Plant plant{.altitude_m = 42.0f, .climb_mps = 0.0f};
    float acc_up = 0.0f;

    fc::ModeManager manager{42.0f, 210.0f};
    manager.set_armed(true);
    manager.set_mission_target(80.0f);

    fc::AltitudeFusion fusion{1.2f, 0.6f};
    fc::crsf::Link link{0ms};
    auto switch_pos = fc::crsf::SwitchPos::Low;
    float prev_out = kHoverThrottle;

    for (int step = 0; step <= 750; ++step) {
        const Millis now{step * 20};
        const float t = static_cast<float>(step) * kDt;

        // Пульт: газ 56 %, тумблер AUX1 у середнє положення на 5-й секунді
        // і у верхнє — на 10-й.
        std::uint16_t aux1 = 191;
        if (step >= 500) aux1 = 1792;
        else if (step >= 250) aux1 = 992;

        const auto frame = fc::crsf::pack(make_tx(kHoverThrottle, aux1, false));
        static_cast<void>(link.feed(frame, now));
        link.tick(now);

        fusion.update(plant.altitude_m, acc_up, kDt);
        const fc::VehicleState state{.altitude_m = fusion.altitude(),
                                     .climb_mps = fusion.climb_rate(),
                                     .heading_deg = 90.0f};

        switch_pos = fc::crsf::switch_position(link.channels().microseconds(4), switch_pos);
        if (const auto want = mode_from_switch(switch_pos); want != manager.mode()) {
            const auto from = manager.mode();
            if (manager.request_mode(want, state))
                std::cout << std::format(">>> [t={:.1f}s] ПЕРЕМИКАННЯ: {} -> {} <<<\n",
                                         t, fc::to_string(from), fc::to_string(want));
            else
                std::cout << std::format(">>> [t={:.1f}s] ВІДМОВА: захоплення неможливе <<<\n", t);
        }

        const fc::PilotInput pilot{.throttle = link.channels().unit(2),
                                   .force_override = link.channels().microseconds(5) > 1700.0f,
                                   .valid = !link.failsafe()};
        const auto out = manager.step(pilot, state, kDt);
        const float du = std::fabs(out.throttle - prev_out);

        if (step == 249 || step == 250 || step == 251 ||
            step == 499 || step == 500 || step == 501) {
            const float integral = manager.mode() == fc::FlightMode::Manual
                                       ? 0.0f
                                       : manager.active_pid().integral();
            std::cout << std::format("{:5.2f}  | {:<12} | {:8.2f}  | {:8.6f} | {:10.6f} | {:9.6f}\n",
                                     t, fc::to_string(manager.mode()), state.altitude_m,
                                     out.throttle, du, integral);
        }

        acc_up = plant.step(out.throttle, kDt);
        prev_out = out.throttle;
    }

    std::cout << std::format("Кадрів прийнято: {}, помилок CRC: {}, зауважень до захоплення: {}\n\n",
                             link.frames_ok(), link.crc_errors(), manager.handover_warnings());
}

// ── Сценарій 2: підхоплення ручки при поверненні в ручний режим ──────────
void scenario_stick_matching()
{
    std::cout << "=== Сценарій 2: Stick Matching при ALT_HOLD -> MANUAL ===\n";

    fc::ModeManager manager{40.0f, 0.0f};
    manager.set_armed(true);

    const fc::VehicleState state{.altitude_m = 40.0f, .climb_mps = 0.0f, .heading_deg = 0.0f};
    fc::PilotInput pilot{.throttle = kHoverThrottle, .force_override = false, .valid = true};

    // Секунда ручного польоту, щоб на приводі стояло 56 %
    for (int i = 0; i < 50; ++i) static_cast<void>(manager.step(pilot, state, kDt));
    static_cast<void>(manager.request_mode(fc::FlightMode::AltHold, state));
    for (int i = 0; i < 50; ++i) static_cast<void>(manager.step(pilot, state, kDt));

    // Пілот, поки летіли в автоматі, зсунув ручку майже до нуля
    pilot.throttle = 0.20f;
    static_cast<void>(manager.request_mode(fc::FlightMode::Manual, state));
    std::cout << std::format("Ручка {:.2f}, тяга на приводі {:.2f} — керування утримано\n",
                             pilot.throttle, manager.held_output());

    std::cout << "Крок | Ручка | Вихід | Підказка\n";
    for (int i = 0; i < 60; ++i) {
        if (i >= 5 && pilot.throttle < 1.0f) pilot.throttle += 0.01f;   // пілот піднімає
        const auto out = manager.step(pilot, state, kDt);
        if (i % 5 == 0 || out.hint == fc::StickHint::Matched)
            std::cout << std::format("{:4} | {:5.2f} | {:5.2f} | {}\n",
                                     i, pilot.throttle, out.throttle, fc::to_string(out.hint));
        if (out.hint == fc::StickHint::Matched) break;
    }

    // Те саме, але пілот тисне силове перехоплення — тяга падає одразу
    static_cast<void>(manager.request_mode(fc::FlightMode::AltHold, state));
    static_cast<void>(manager.step(pilot, state, kDt));
    pilot.throttle = 0.20f;
    static_cast<void>(manager.request_mode(fc::FlightMode::Manual, state));
    pilot.force_override = true;
    const auto forced = manager.step(pilot, state, kDt);
    std::cout << std::format("Force Override: ручка {:.2f} -> вихід {:.2f} ({})\n\n",
                             pilot.throttle, forced.throttle, fc::to_string(forced.hint));
}

// ── Сценарій 3: аварійний перехід при втраті зв'язку ─────────────────────
void scenario_failsafe()
{
    std::cout << "=== Сценарій 3: Failsafe -> повернення на базу ===\n";

    Plant plant{.altitude_m = 60.0f, .climb_mps = 0.0f};
    float acc_up = 0.0f;

    fc::ModeManager manager{40.0f, 210.0f};   // база: висота 40 м, азимут 210°
    manager.set_armed(true);

    fc::AltitudeFusion fusion{1.2f, 0.6f};
    fc::crsf::Link link{0ms};

    float heading = 30.0f;
    float prev_out = kHoverThrottle;
    bool announced = false;

    for (int step = 0; step <= 600; ++step) {
        const Millis now{step * 20};
        const float t = static_cast<float>(step) * kDt;

        // Після 6-ї секунди приймач мовчить: кадрів більше не подаємо.
        if (step < 300) {
            const auto frame = fc::crsf::pack(make_tx(kHoverThrottle, 992, false));
            static_cast<void>(link.feed(frame, now));
        }
        const bool lost = link.tick(now);

        // На 2-й секунді барометр видає викид — фільтр мусить його відкинути.
        const float baro = step == 100 ? plant.altitude_m + 60.0f : plant.altitude_m;
        fusion.update(baro, acc_up, kDt);

        const fc::VehicleState state{.altitude_m = fusion.altitude(),
                                     .climb_mps = fusion.climb_rate(),
                                     .heading_deg = heading};

        if (step == 1) static_cast<void>(manager.request_mode(fc::FlightMode::AltHold, state));

        if (lost && !manager.failsafe()) {
            manager.enter_failsafe(state);
            std::cout << std::format(">>> [t={:.2f}s] FAILSAFE: {} мс без кадру -> повернення на базу\n",
                                     t, link.silence(now).count());
        }

        const fc::PilotInput pilot{.throttle = link.channels().unit(2),
                                   .force_override = false,
                                   .valid = !link.failsafe()};
        const auto out = manager.step(pilot, state, kDt);

        if (lost && !announced) {
            std::cout << std::format("Стрибок тяги на переході: dU = {:.6f}\n",
                                     std::fabs(out.throttle - prev_out));
            announced = true;
        }
        if (step % 50 == 0 && step >= 300)
            std::cout << std::format("t={:5.2f} | курс {:6.1f}° -> ціль 210° | висота {:6.2f} | тяга {:.4f}\n",
                                     t, out.heading_cmd_deg, state.altitude_m, out.throttle);

        heading = out.heading_cmd_deg;   // борт іде за командою курсу
        acc_up = plant.step(out.throttle, kDt);
        prev_out = out.throttle;
    }

    std::cout << std::format("Відкинуто викидів барометра: {}\n", fusion.rejected());
}

}  // namespace

int main()
{
    scenario_mode_switch();
    scenario_stick_matching();
    scenario_failsafe();
    return 0;
}
