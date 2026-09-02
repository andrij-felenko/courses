#include "bumpless/pid.hpp"

#include "bumpless/ramp.hpp"

#include <array>
#include <cmath>
#include <string_view>
#include <utility>

namespace bumpless {

std::string describe(Fault faults)
{
    if (faults == Fault::None) {
        return "-";
    }

    static constexpr std::array<std::pair<Fault, std::string_view>, 5> names{{
        {Fault::BadMeasurement, "BAD_MEASUREMENT"},
        {Fault::BadDt, "BAD_DT"},
        {Fault::PreloadClamped, "PRELOAD_CLAMPED"},
        {Fault::NotReady, "NOT_READY"},
        {Fault::OutputSaturated, "OUTPUT_SATURATED"},
    }};

    std::string out;
    for (const auto& [flag, name] : names) {
        if (!contains(faults, flag)) {
            continue;
        }
        if (!out.empty()) {
            out += '|';
        }
        out += name;
    }
    return out;
}

void BumplessPidController::reset() noexcept
{
    integral_ = 0.0f;
    prev_measurement_ = 0.0f;
    deriv_filt_ = 0.0f;
    target_setpoint_ = 0.0f;
    current_setpoint_ = 0.0f;
    last_output_ = 0.0f;
    is_initialized_ = false;
    faults_ = Fault::None;
}

void BumplessPidController::start_naive(float setpoint) noexcept
{
    reset();
    target_setpoint_ = setpoint;
    current_setpoint_ = setpoint;
    is_initialized_ = true;
}

void BumplessPidController::preload(float measurement, float hold_setpoint,
                                    float target_setpoint, float prev_output) noexcept
{
    if (!std::isfinite(measurement) || !std::isfinite(prev_output) ||
        !std::isfinite(hold_setpoint) || !std::isfinite(target_setpoint)) {
        // Захоплення не відбулося. Диспетчер режимів мусить побачити прапорець
        // і лишитися в попередньому режимі: краще старий контур, ніж контур,
        // передзавантажений сміттям.
        faults_ |= Fault::BadMeasurement;
        return;
    }

    // Крок 1. Відстеження уставки: у типовому виклику hold_setpoint і є
    // поточним виміром, тож помилка на першому такті дорівнює нулю.
    current_setpoint_ = hold_setpoint;
    target_setpoint_ = target_setpoint;

    // Крок 2. Пам'ять диференціатора прирівнюємо до факту.
    prev_measurement_ = measurement;
    deriv_filt_ = 0.0f;

    const float error = current_setpoint_ - measurement;
    const float p_term = cfg_.kp * error;
    const float d_term = -cfg_.kd * deriv_filt_; // тотожно 0, лишаємо у формулі
    const float ff_term = cfg_.kff * current_setpoint_;

    // Крок 3. I(0+) = u_prev - P - D - FF.
    const float needed_i = prev_output - p_term - d_term - ff_term;

    const auto limits = cfg_.safe_integral_limits();
    integral_ = std::clamp(needed_i, limits.lo, limits.hi);

    if (std::abs(integral_ - needed_i) > 1e-6f) {
        // Привід стояв у насиченні: точний перехід неможливий, залишковий
        // стрибок дорівнює зрізаній частині. Телеметрія має це знати.
        faults_ |= Fault::PreloadClamped;
    }

    last_output_ = std::clamp(p_term + integral_ + d_term + ff_term,
                              cfg_.out_min, cfg_.out_max);
    is_initialized_ = true;
}

void BumplessPidController::handover(float current_measurement, float target_setpoint,
                                     float prev_actuator_output) noexcept
{
    preload(current_measurement, current_measurement, target_setpoint, prev_actuator_output);
}

void BumplessPidController::handover_hold(float current_measurement, float hold_setpoint,
                                          float target_setpoint,
                                          float prev_actuator_output) noexcept
{
    preload(current_measurement, hold_setpoint, target_setpoint, prev_actuator_output);
}

float BumplessPidController::update(float measurement, float dt) noexcept
{
    if (!is_initialized_) {
        faults_ |= Fault::NotReady;
        return last_output_;
    }
    if (!std::isfinite(measurement)) {
        // Збій шини давача. Інтегратор не рухаємо взагалі: тримаємо останній
        // справний вихід — завмерла поверхня краща за перекладку в NaN.
        faults_ |= Fault::BadMeasurement;
        return last_output_;
    }
    if (!std::isfinite(dt) || dt <= 0.0f) {
        faults_ |= Fault::BadDt;
        return last_output_;
    }
    if (dt > kMaxDt) {
        faults_ |= Fault::BadDt;
        dt = kMaxDt;
    }

    // 1. Ремпінг уставки.
    current_setpoint_ = slew_step(current_setpoint_, target_setpoint_,
                                  cfg_.slew_rate_max * dt);

    // 2. Пропорційна складова.
    const float error = current_setpoint_ - measurement;
    const float p_term = cfg_.kp * error;

    // 3. Похідна ВИМІРУ, ще й згладжена: диференціювання помилки давало б
    //    удар на кожній зміні уставки, а сира похідна — на кожному шумі.
    const float d_raw = (measurement - prev_measurement_) / dt;
    prev_measurement_ = measurement;
    const float alpha = (cfg_.d_lpf_tau > 0.0f) ? dt / (dt + cfg_.d_lpf_tau) : 1.0f;
    deriv_filt_ += alpha * (d_raw - deriv_filt_);
    const float d_term = -cfg_.kd * deriv_filt_;

    // 4. Пряме прогнозне керування.
    const float ff_term = cfg_.kff * current_setpoint_;

    // 5. Пробне інтегрування — у стан його ще не пишемо.
    const float i_candidate = std::clamp(integral_ + cfg_.ki * error * dt,
                                         cfg_.i_min, cfg_.i_max);
    const float u_raw = p_term + i_candidate + d_term + ff_term;

    // 6. Анти-віндап затиском: приймаємо новий інтеграл лише тоді, коли він
    //    не штовхає вже насичений вихід іще далі за упор.
    const bool pushing_up = (u_raw > cfg_.out_max) && (i_candidate > integral_);
    const bool pushing_down = (u_raw < cfg_.out_min) && (i_candidate < integral_);
    if (!pushing_up && !pushing_down) {
        integral_ = i_candidate;
    }

    // 7. Фізична межа ходу приводу.
    const float u_final = std::clamp(u_raw, cfg_.out_min, cfg_.out_max);
    if (u_final != u_raw) {
        faults_ |= Fault::OutputSaturated;
    }

    last_output_ = u_final;
    return u_final;
}

} // namespace bumpless
