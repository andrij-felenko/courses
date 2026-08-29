#include "supervisor.hpp"

#include <algorithm>
#include <cmath>

namespace safety {
namespace {

bool finite(float v) noexcept { return std::isfinite(v); }

} // namespace

std::expected<void, Fault> Supervisor::submit_plan(const Command& cmd) noexcept
{
    if (!finite(cmd.vx) || !finite(cmd.vy) || !finite(cmd.yaw_rate)) {
        log_.record(uptime_, Status::Clamped, Reason::BadPlan, 0.0f);
        return std::unexpected(Fault::NonFiniteCommand);
    }

    candidate_ = cmd;
    plan_age_ = Seconds::zero();
    return {};
}

Outcome Supervisor::engage_brake(Seconds dt, Reason reason, float value) noexcept
{
    const float decel = limits::kMaxBrakeAccel * dt.count();
    last_out_vx_ = std::max(0.0f, last_out_vx_ - decel);

    log_.record(uptime_, Status::BrakeEngaged, reason, value);
    return Outcome{Command{last_out_vx_, 0.0f, 0.0f}, Status::BrakeEngaged, reason};
}

// Fail-closed: коли далекомір мовчить, бар'єр не вважає простір вільним, а віднімає
// від останньої достовірної дистанції пройдений шлях. Оцінка з часом лише гіршає.
float Supervisor::update_distance_estimate(const std::optional<float>& measured, Seconds dt) noexcept
{
    if (measured && finite(*measured) && *measured >= 0.0f) {
        dr_dist_m_ = *measured;
        blind_for_ = Seconds::zero();
        dist_trusted_ = true;
        return dr_dist_m_;
    }

    dr_dist_m_ = std::max(0.0f, dr_dist_m_ - last_out_vx_ * dt.count());
    blind_for_ += dt;
    dist_trusted_ = false;
    return dr_dist_m_;
}

std::expected<Outcome, Fault> Supervisor::step(const Sensors& sn, Seconds dt) noexcept
{
    if (!finite(dt.count()) || dt <= Seconds::zero()) {
        last_out_vx_ = 0.0f;
        return std::unexpected(Fault::InvalidTimeStep);
    }

    uptime_ += dt;
    plan_age_ += dt;

    // 1. Апаратна кнопка стоїть вище за будь-яку логіку
    if (sn.emergency_stop) {
        last_out_vx_ = 0.0f;
        log_.record(uptime_, Status::EmergencyStop, Reason::EmergencyStop, 0.0f);
        return Outcome{Command{}, Status::EmergencyStop, Reason::EmergencyStop};
    }

    // 2. Дистанція: або вимір, або консервативне числення
    const float dist = update_distance_estimate(sn.obstacle_dist_m, dt);

    // 3. Крен; зіпсований вимір кута — теж підстава гальмувати
    if (!finite(sn.tilt_rad) || !finite(sn.tilt_limit_rad) || sn.tilt_limit_rad <= 0.0f) {
        return engage_brake(dt, Reason::SensorLost, sn.tilt_rad);
    }
    if (sn.tilt_rad >= sn.tilt_limit_rad) {
        return engage_brake(dt, Reason::Tilt, sn.tilt_rad);
    }

    // 4. Сторож планувальника: уставка застаріла — керуємо самі
    if (plan_age_ > limits::kWatchdogMaxAge) {
        return engage_brake(dt, Reason::PlannerTimeout, plan_age_.count());
    }

    // 5. Невизначеність дистанції довша за допуск — плавна зупинка
    if (!dist_trusted_ && blind_for_ >= limits::kSensorHoldMax) {
        return engage_brake(dt, Reason::SensorLost, blind_for_.count());
    }

    // Далі — проєкція уставки на допустиму область. Кожен крок лише зменшує
    // дозволене, тож остання спрацьована причина і є найтіснішою.
    float target_vx = std::max(0.0f, candidate_.vx); // задній хід у цій моделі не розглядаємо
    float target_yaw = candidate_.yaw_rate;
    Reason reason = Reason::None;
    float violated = 0.0f;

    // 6. Гальмівний бар'єр за дистанцією
    const float stop_dist = (target_vx * target_vx) / (2.0f * limits::kMaxBrakeAccel)
                          + target_vx * limits::kLatencyPadSec
                          + limits::kSafetyMarginM;
    if (dist < stop_dist) {
        const float available = dist - limits::kSafetyMarginM;
        const float v_max_safe = (available <= 0.0f)
                               ? 0.0f
                               : std::sqrt(2.0f * limits::kMaxBrakeAccel * available);
        if (target_vx > v_max_safe) {
            target_vx = v_max_safe;
            reason = Reason::Obstacle;
            violated = dist;
        }
    }

    // 7. Просідання шини: униз ідуть і швидкість, і темп розгону
    float v_factor = 1.0f;
    if (!sn.battery_voltage || !finite(*sn.battery_voltage)) {
        v_factor = 0.0f; // вимірювача напруги нема — рахуємо найгірше
        reason = Reason::SensorLost;
        violated = 0.0f;
    } else if (*sn.battery_voltage < limits::kNominalVoltageV) {
        const float span = limits::kNominalVoltageV - limits::kCriticalVoltageV;
        v_factor = std::clamp((*sn.battery_voltage - limits::kCriticalVoltageV) / span, 0.0f, 1.0f);
    }
    if (v_factor < 1.0f) {
        const float max_bat_vx = limits::kMaxSpeedMps * v_factor;
        if (target_vx > max_bat_vx) {
            target_vx = max_bat_vx;
            reason = Reason::Battery;
            violated = sn.battery_voltage.value_or(0.0f);
        }
    }

    // 8. Підхід до критичного крену: тиснемо рискання й хід разом
    const float tilt_warn = sn.tilt_limit_rad * limits::kTiltWarnFraction;
    if (sn.tilt_rad > tilt_warn) {
        const float headroom = sn.tilt_limit_rad - tilt_warn;
        const float scale = std::clamp((sn.tilt_limit_rad - sn.tilt_rad) / headroom, 0.0f, 1.0f);
        target_yaw *= scale;
        target_vx *= scale;
        reason = Reason::Tilt;
        violated = sn.tilt_rad;
    }

    // 9. Абсолютні межі приводів
    if (target_vx > limits::kMaxSpeedMps) {
        target_vx = limits::kMaxSpeedMps;
        reason = Reason::SpeedLimit;
        violated = candidate_.vx;
    }
    if (const float yaw = std::clamp(target_yaw, -limits::kMaxYawRateRadps, limits::kMaxYawRateRadps);
        yaw != target_yaw) {
        target_yaw = yaw;
        if (reason == Reason::None) {
            reason = Reason::YawLimit;
            violated = candidate_.yaw_rate;
        }
    }

    // 10. Темп розгону за струмовим бюджетом. Сповільнення не обмежуємо:
    //     у бік безпеки фільтр працює миттєво.
    const float accel_cap = limits::kMaxAccel * v_factor;
    if (const float ceiling = last_out_vx_ + accel_cap * dt.count(); target_vx > ceiling) {
        target_vx = ceiling;
        if (reason == Reason::None) {
            reason = Reason::AccelLimit;
            violated = accel_cap;
        }
    }

    last_out_vx_ = target_vx;
    const Status status = (reason == Reason::None) ? Status::PassThrough : Status::Clamped;
    log_.record(uptime_, status, reason, violated);

    return Outcome{Command{target_vx, candidate_.vy, target_yaw}, status, reason};
}

} // namespace safety
