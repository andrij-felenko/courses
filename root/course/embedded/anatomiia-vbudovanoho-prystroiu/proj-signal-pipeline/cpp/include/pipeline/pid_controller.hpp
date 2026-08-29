#pragma once

#include <algorithm>
#include <cstdint>

namespace pipeline {

/// Арифметика з фіксованою комою Q8.8.
namespace fp {

using q8 = std::int32_t;

inline constexpr q8 kOne = 256;
inline constexpr q8 kLimit = 32767; ///< стеля, з якої рахований бюджет множення

/// Коефіцієнт із десяткового запису у Q8.8 — і жодного float у прошивці:
/// consteval означає, що інакше як під час збирання це не обчислиться,
/// а вихід за межі формату стає помилкою компіляції, а не тихим зсувом знака.
consteval q8 from_double(double v)
{
    if (v < 0.0 || v * kOne > static_cast<double>(kLimit)) {
        throw "коефіцієнт не вміщується у Q8.8";
    }
    return static_cast<q8>(v * kOne + 0.5);
}

/// Множення на коефіцієнт Q8.8 з поверненням у Q0.
/// Зсув, а не ділення: ділення на Cortex-M0+ — бібліотечна підпрограма.
/// Для від'ємних чисел зсув округлює вниз, тобто занижує результат
/// щонайбільше на одну одиницю виходу.
constexpr std::int32_t mul(q8 coeff, std::int32_t x) noexcept
{
    return (coeff * x) >> 8;
}

} // namespace fp

struct Gains {
    fp::q8 kp;
    fp::q8 ki;
    fp::q8 kd;
};

struct Limits {
    std::int32_t min;
    std::int32_t max;
};

/// Дискретний ПІД-регулятор на цілих числах.
/// Період квантування в коефіцієнтах зашитий і мусить бути незмінним —
/// об'єкт викликають виключно з переривання таймера.
class PidController {
public:
    constexpr PidController(Gains gains, Limits limits) noexcept
        : gains_{gains}, limits_{limits}, integral_limit_{integral_limit_for(gains, limits)}
    {
    }

    constexpr std::int32_t update(std::int32_t setpoint, std::int32_t measured) noexcept
    {
        const std::int32_t error = setpoint - measured;

        const std::int32_t p_term = fp::mul(gains_.kp, error);

        // Anti-Windup. Обмежуємо саму суму, і саме ДО множення: так вона
        // фізично не може дорости до переповнення int32 — а переповнення тут
        // страшніше за насичення, бо міняє знак і вимикає навантаження там,
        // де його треба тримати на максимумі.
        integral_ = std::clamp(integral_ + error, -integral_limit_, integral_limit_);
        const std::int32_t i_term = fp::mul(gains_.ki, integral_);

        // На першому кроці попередньої помилки немає: нуль дав би удар
        // диференційної складової на всю шкалу з нічого.
        std::int32_t d_term = 0;
        if (has_prev_) {
            d_term = fp::mul(gains_.kd, error - prev_error_);
        }
        prev_error_ = error;
        has_prev_ = true;

        return std::clamp(p_term + i_term + d_term, limits_.min, limits_.max);
    }

    constexpr void reset() noexcept
    {
        integral_ = 0;
        prev_error_ = 0;
        has_prev_ = false;
    }

    [[nodiscard]] constexpr std::int32_t integral() const noexcept { return integral_; }

private:
    /// Межа накопичувача: більше, ніж треба інтегральній складовій, щоб самій
    /// покрити всю вихідну шкалу, сумі рости немає сенсу. Рахується під час
    /// збирання — у прошивці це готова стала.
    static constexpr std::int32_t integral_limit_for(Gains g, Limits l) noexcept
    {
        if (g.ki <= 0) {
            return 0;
        }
        return static_cast<std::int32_t>(
            (static_cast<std::int64_t>(l.max) * fp::kOne) / g.ki);
    }

    Gains gains_;
    Limits limits_;
    std::int32_t integral_limit_;
    std::int32_t integral_{0};
    std::int32_t prev_error_{0};
    bool has_prev_{false};
};

} // namespace pipeline
