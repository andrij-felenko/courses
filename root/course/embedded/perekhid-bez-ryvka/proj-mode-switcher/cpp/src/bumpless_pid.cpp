#include "bumpless_pid.hpp"

#include <algorithm>
#include <cmath>

namespace fc {

std::expected<float, HandoverError>
BumplessPid::handover(float meas, std::optional<float> meas_rate,
                      float target_sp, float prev_out) noexcept
{
    if (!std::isfinite(meas)) {
        ++bad_samples_;
        ready_ = false;
        return std::unexpected{HandoverError::SensorUnusable};
    }
    if (!std::isfinite(prev_out)) {
        ready_ = false;
        return std::unexpected{HandoverError::OutputUnusable};
    }

    const float rate = meas_rate.value_or(0.0f);

    current_sp_ = meas;   // уставка = поточний вимір, отже помилка рівно нуль
    target_sp_ = std::isfinite(target_sp) ? target_sp : meas;
    prev_meas_ = meas;

    const float p_term = gains_.kp * (current_sp_ - meas);   // тотожний нуль
    const float ff_term = gains_.kff * current_sp_;
    const float d_term = -gains_.kd * rate;  // саме стільки дасть D на першому такті

    // Інтегратор добираємо так, щоб сума гілок дала рівно те, що вже стоїть
    // на приводі: у цьому вся передача повноважень.
    integral_ = std::clamp(prev_out - p_term - ff_term - d_term,
                           gains_.i_min, gains_.i_max);

    last_out_ = std::clamp(p_term + integral_ + d_term + ff_term,
                           gains_.out_min, gains_.out_max);
    ready_ = true;
    return last_out_ - prev_out;
}

void BumplessPid::retarget(float target_sp) noexcept
{
    if (std::isfinite(target_sp)) target_sp_ = target_sp;
}

float BumplessPid::update(float meas, std::optional<float> meas_rate, float dt) noexcept
{
    if (!ready_ || !(dt > 0.0f)) return last_out_;
    if (!std::isfinite(meas)) {
        // Пропав вимір — тримаємо останній вихід, сміття не інтегруємо.
        ++bad_samples_;
        return last_out_;
    }

    // Ремпінг уставки: ціль може бути далеко, але йдемо до неї обмеженим
    // темпом, інакше ривок просто переїде з перемикання на нову ціль.
    if (gains_.slew_rate_max > 0.0f) {
        const float max_step = gains_.slew_rate_max * dt;
        current_sp_ += std::clamp(target_sp_ - current_sp_, -max_step, max_step);
    } else {
        current_sp_ = target_sp_;
    }

    const float err = current_sp_ - meas;
    const float p_term = gains_.kp * err;

    const float rate = meas_rate.value_or((meas - prev_meas_) / dt);
    prev_meas_ = meas;
    const float d_term = -gains_.kd * rate;   // похідна по виміру, не по помилці

    const float ff_term = gains_.kff * current_sp_;
    const float cand_i = integral_ + gains_.ki * err * dt;
    const float u_raw = p_term + cand_i + d_term + ff_term;

    // Умовна інтеграція: вихід уперся, а помилка штовхає далі в той самий
    // бік — не наливаємо, бо потім інтегратор не віддасть керування назад.
    const bool sat_hi = (u_raw > gains_.out_max) && (err > 0.0f);
    const bool sat_lo = (u_raw < gains_.out_min) && (err < 0.0f);
    if (!sat_hi && !sat_lo) integral_ = std::clamp(cand_i, gains_.i_min, gains_.i_max);

    last_out_ = std::clamp(u_raw, gains_.out_min, gains_.out_max);
    return last_out_;
}

}  // namespace fc
