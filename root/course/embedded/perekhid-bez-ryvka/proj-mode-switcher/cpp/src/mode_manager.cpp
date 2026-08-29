#include "mode_manager.hpp"

#include <algorithm>
#include <cmath>

#include "dshot.hpp"

namespace fc {
namespace {

constexpr PidGains kAltHoldGains{   // спокійний контур, набір не швидше 2 м/с
    .kp = 0.08f, .ki = 0.04f, .kd = 0.02f, .kff = 0.0f,
    .out_min = 0.0f, .out_max = 1.0f,
    .i_min = 0.0f, .i_max = 0.9f,
    .slew_rate_max = 2.0f};

constexpr PidGains kMissionGains{   // жвавіший, набір до 3.5 м/с
    .kp = 0.12f, .ki = 0.05f, .kd = 0.03f, .kff = 0.0f,
    .out_min = 0.0f, .out_max = 1.0f,
    .i_min = 0.0f, .i_max = 0.9f,
    .slew_rate_max = 3.5f};

float wrap180(float angle) noexcept
{
    angle = std::fmod(angle + 180.0f, 360.0f);
    if (angle < 0.0f) angle += 360.0f;
    return angle - 180.0f;
}

float heading_step(float current, float target, float rate_dps, float dt) noexcept
{
    const float max_step = rate_dps * dt;
    float result = current + std::clamp(wrap180(target - current), -max_step, max_step);
    if (result < 0.0f) result += 360.0f;
    if (result >= 360.0f) result -= 360.0f;
    return result;
}

}  // namespace

ModeManager::ModeManager(float home_alt_m, float home_bearing_deg) noexcept
    : alt_hold_{kAltHoldGains},
      mission_{kMissionGains},
      mission_alt_m_{home_alt_m},
      home_alt_m_{home_alt_m},
      home_bearing_deg_{home_bearing_deg} {}

const BumplessPid& ModeManager::active_pid() const noexcept
{
    return mode_ == FlightMode::AutoMission ? mission_ : alt_hold_;
}

void ModeManager::set_mission_target(float altitude_m) noexcept
{
    if (!std::isfinite(altitude_m)) return;
    mission_alt_m_ = altitude_m;
    if (mode_ == FlightMode::AutoMission) mission_.retarget(altitude_m);
}

std::expected<float, HandoverError>
ModeManager::request_mode(FlightMode mode, const VehicleState& state) noexcept
{
    if (mode == mode_) return 0.0f;

    const float prev_out = last_out_;
    std::expected<float, HandoverError> residual{0.0f};

    switch (mode) {
    case FlightMode::Manual:
        // Ручка пілота може стояти будь-де. Доки вона не зійдеться з
        // поточною тягою, керування тримає диспетчер.
        stick_hold_ = true;
        u_hold_ = prev_out;
        break;

    case FlightMode::AltHold:
        residual = alt_hold_.handover(state.altitude_m, state.climb_mps,
                                      state.altitude_m, prev_out);
        break;

    case FlightMode::AutoMission:
        // Стартуємо з поточної висоти, ціль — точка маршруту; ремпінг
        // уставки доведе туди без ривка.
        residual = mission_.handover(state.altitude_m, state.climb_mps,
                                     mission_alt_m_, prev_out);
        heading_cmd_deg_ = state.heading_deg;
        break;
    }

    if (!residual) {
        // Захоплення не вийшло — лишаємось у чинному режимі: це безпечніше
        // за перехід із невідомим станом інтегратора.
        ++rejected_switches_;
        return residual;
    }
    if (std::fabs(*residual) > kHandoverTolerance) ++handover_warnings_;

    mode_ = mode;
    return residual;
}

void ModeManager::enter_failsafe(const VehicleState& state) noexcept
{
    if (failsafe_) return;
    failsafe_ = true;

    // Висота старту стає ціллю, поточний курс — початком розвороту.
    mission_alt_m_ = home_alt_m_;
    if (mode_ == FlightMode::AutoMission) {
        mission_.retarget(mission_alt_m_);
    } else {
        static_cast<void>(request_mode(FlightMode::AutoMission, state));
    }
    heading_cmd_deg_ = state.heading_deg;
}

void ModeManager::clear_failsafe() noexcept
{
    // Лінк ожив — прапорець знімаємо, але режим лишається автоматичним:
    // керування повертає пілот тумблером, а не поява одного пакета.
    failsafe_ = false;
}

ModeOutput ModeManager::step(const PilotInput& pilot, const VehicleState& state,
                             float dt) noexcept
{
    ModeOutput out{};
    float u = last_out_;

    switch (mode_) {
    case FlightMode::Manual:
        if (!pilot.valid) {
            u = last_out_;   // лінк мовчить — тримаємо останнє до failsafe
        } else if (stick_hold_) {
            const float diff = pilot.throttle - u_hold_;
            if (pilot.force_override || std::fabs(diff) <= kStickMatchWindow) {
                stick_hold_ = false;
                u = pilot.throttle;
                out.hint = StickHint::Matched;
            } else {
                u = u_hold_;   // віртуальний автотрим
                out.hint = diff < 0.0f ? StickHint::PushUp : StickHint::PushDown;
            }
        } else {
            u = pilot.throttle;
        }
        break;

    case FlightMode::AltHold:
        u = alt_hold_.update(state.altitude_m, state.climb_mps, dt);
        break;

    case FlightMode::AutoMission:
        u = mission_.update(state.altitude_m, state.climb_mps, dt);
        break;
    }

    if (!std::isfinite(u)) u = last_out_;

    // Курс: у автоматі при failsafe розвертаємось на базу обмеженим темпом,
    // поза failsafe тримаємо той, з яким увійшли.
    if (mode_ == FlightMode::AutoMission) {
        const float target = failsafe_ ? home_bearing_deg_ : heading_cmd_deg_;
        heading_cmd_deg_ = heading_step(heading_cmd_deg_, target, kYawRateMaxDps, dt);
    } else {
        heading_cmd_deg_ = state.heading_deg;
    }

    last_out_ = u;
    out.throttle = u;
    out.dshot_value = dshot::throttle_value(u, armed_);
    out.dshot_packet = dshot::packet(out.dshot_value, false);
    out.heading_cmd_deg = heading_cmd_deg_;
    return out;
}

std::string_view to_string(FlightMode mode) noexcept
{
    switch (mode) {
    case FlightMode::Manual: return "MANUAL";
    case FlightMode::AltHold: return "ALT_HOLD";
    case FlightMode::AutoMission: return "AUTO_MISSION";
    }
    return "?";
}

std::string_view to_string(StickHint hint) noexcept
{
    switch (hint) {
    case StickHint::None: return "-";
    case StickHint::PushUp: return "ПІДНІМИ РУЧКУ";
    case StickHint::PushDown: return "ОПУСТИ РУЧКУ";
    case StickHint::Matched: return "КЕРУВАННЯ ВІДДАНО";
    }
    return "?";
}

}  // namespace fc
