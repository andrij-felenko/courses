#pragma once

/*
 * Числові дрібниці контуру. Усе constexpr/inline: на Cortex-M
 * розгортається в одну-дві інструкції FPU.
 */

#include <algorithm>
#include <cmath>

namespace control::num {

/*
 * Затиск у межі. std::clamp вимагає lo <= hi — конфігурацію перевіряють
 * при створенні регулятора. NaN сюди не доходить: його ловлять раніше.
 */
[[nodiscard]] constexpr float clamp_to(float value, float lo, float hi) noexcept
{
    return std::clamp(value, lo, hi);
}

[[nodiscard]] inline bool finite(float value) noexcept
{
    return std::isfinite(value);
}

struct SlewResult {
    float value{0.0f};
    bool limited{false};   ///< крок справді вперся в обмеження темпу
};

/*
 * Крок обмежувача темпу уставки. rate <= 0 вимикає ремпінг:
 * уставка стрибає в ціль одразу.
 */
[[nodiscard]] inline SlewResult slew_step(float current, float target,
                                          float rate, float dt) noexcept
{
    if (!finite(target)) {
        // Уставку зіпсували ззовні — тримаємо те, що є.
        return {current, false};
    }
    if (!(rate > 0.0f)) {
        return {target, false};
    }

    const float max_step = rate * dt;
    const float delta = target - current;
    if (delta > max_step) {
        return {current + max_step, true};
    }
    if (delta < -max_step) {
        return {current - max_step, true};
    }
    return {target, false};
}

} // namespace control::num
