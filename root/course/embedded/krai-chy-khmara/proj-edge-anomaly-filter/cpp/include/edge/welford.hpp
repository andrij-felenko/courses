#pragma once

#include <cmath>
#include <cstdint>
#include <limits>

namespace edge {

/**
 * Потокова статистика за алгоритмом Велфорда (B. P. Welford, 1962).
 *
 * Наївне E[X^2] - (E[X])^2 на float для 230.0 В із шумом 0.1 В віднімає два
 * числа близько 52900, щоб дістати 0.01: 24 бітів мантиси на це не вистачає,
 * і дисперсія виходить від'ємною. Велфорд працює з відхиленнями, тому
 * великий постійний доданок у різницю не потрапляє взагалі.
 */
class Welford {
public:
    constexpr Welford() noexcept = default;

    /// Не-скінченні вибірки ігноруються: одна NaN назавжди отруїла б стан.
    void update(float x) noexcept
    {
        if (!std::isfinite(x)) {
            return;
        }
        // Насичення лічильника: за 1.4 року на 100 Гц uint32 обгорнувся б у нуль,
        // і наступне ж оновлення середнього поділило б на нуль.
        if (count_ == std::numeric_limits<std::uint32_t>::max()) {
            return;
        }
        ++count_;

        const float delta = x - mean_;
        mean_ += delta / static_cast<float>(count_);
        const float delta2 = x - mean_;   // уже з НОВИМ середнім — у цьому вся суть
        m2_ += delta * delta2;
    }

    [[nodiscard]] constexpr std::uint32_t count() const noexcept { return count_; }
    [[nodiscard]] constexpr float mean() const noexcept { return mean_; }

    [[nodiscard]] float variance() const noexcept
    {
        if (count_ < 2) {
            return 0.0f;
        }
        // Округлення здатне зіштовхнути m2 трохи нижче нуля — тоді sqrt дав би NaN.
        const float var = m2_ / static_cast<float>(count_ - 1);
        return var > 0.0f ? var : 0.0f;
    }

    [[nodiscard]] float stddev() const noexcept { return std::sqrt(variance()); }

    /// |x - mean| / sigma. Сигнал-константа (обрив давача) дає sigma == 0,
    /// і замість нескінченності повертається безпечний нуль.
    [[nodiscard]] float z_score(float x) const noexcept
    {
        const float sigma = stddev();
        if (sigma < 1e-6f || !std::isfinite(x)) {
            return 0.0f;
        }
        return std::fabs(x - mean_) / sigma;
    }

    constexpr void reset() noexcept
    {
        count_ = 0;
        mean_  = 0.0f;
        m2_    = 0.0f;
    }

private:
    std::uint32_t count_{0};
    float mean_{0.0f};
    float m2_{0.0f};   ///< сума квадратів відхилень від поточного середнього
};

}  // namespace edge
