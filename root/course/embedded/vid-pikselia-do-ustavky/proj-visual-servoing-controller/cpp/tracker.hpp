#pragma once

#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>

namespace servo {

using Seconds = std::chrono::duration<float>;

/* Фільтр Калмана на одну кутову вісь.
 *
 * Стан — [пеленг цілі, кутова швидкість цілі] у нерухомій рамці, тобто в
 * такій, що не крутиться разом з апаратом. Обертання самого апарата живе
 * окремо, в інтегралі гіроскопа: інакше кожен маневр носія фільтр читав би
 * як маневр цілі. */
class BearingTracker {
public:
    struct Config {
        float q_bearing{1e-3f};   /* шум процесу за кутом */
        float q_rate{2.0f};       /* шум процесу за швидкістю — маневр цілі */
        float r_meas{2.3e-6f};    /* дисперсія детектора, рад² */
        float gate_sigma{3.0f};   /* поріг відбраковування інновації */
    };

    struct Estimate {
        float bearing;            /* кут візування в рамці тіла, рад */
        float rate;               /* кутова швидкість цілі, рад/с */
    };

    constexpr explicit BearingTracker(Config cfg = {}) noexcept : cfg_{cfg} {}

    /* Скидаємо лише оцінку цілі: інтеграл гіроскопа далі несе історія курсу. */
    constexpr void acquire() noexcept {
        bearing_ = 0.0f;
        rate_ = 0.0f;
        P_ = kInitialP;
        rejects_ = 0;
        primed_ = false;
    }

    void predict(Seconds dt, float gyro_rate) noexcept {
        const float h = dt.count();
        if (!(h > 0.0f) || h > 0.5f) {
            return;             /* зрив таймера — крок пропускаємо цілком */
        }
        if (std::isfinite(gyro_rate)) {
            body_angle_ += gyro_rate * h;
        }
        if (!primed_) {
            return;
        }

        bearing_ += rate_ * h;

        /* P = F·P·Fᵀ + Q·dt, F = [[1, dt], [0, 1]] */
        const auto p = P_;
        P_[0][0] = p[0][0] + h * (p[1][0] + p[0][1]) + h * h * p[1][1] + cfg_.q_bearing * h;
        P_[0][1] = p[0][1] + h * p[1][1];
        P_[1][0] = p[1][0] + h * p[1][1];
        P_[1][1] = p[1][1] + cfg_.q_rate * h;
    }

    /* Корекція запізнілим кадром: los — кут візування на момент експозиції,
     * body_at_capture — ракурс апарата тоді ж, latency — наскільки стан
     * фільтра встиг випередити цей момент. */
    bool update(float los, float body_at_capture, Seconds latency) noexcept {
        if (!std::isfinite(los) || !std::isfinite(body_at_capture)) {
            return false;
        }
        const float z = los + body_at_capture;

        if (!primed_) {
            bearing_ = z;
            rate_ = 0.0f;
            primed_ = true;
            rejects_ = 0;
            return true;
        }

        const float lag = std::clamp(latency.count(), 0.0f, 1.0f);
        const float innovation = z - (bearing_ - rate_ * lag);
        const float s = P_[0][0] + cfg_.r_meas;
        if (!(s > 1e-9f)) {
            return false;
        }

        /* Детектор інколи перестрибує на сусідній об'єкт — такий кадр гейт
         * відкидає. Але коли промахів набралося поспіль, помиляється фільтр,
         * а не детектор: ціль маневрувала, оцінку сіємо наново. */
        if (innovation * innovation > cfg_.gate_sigma * cfg_.gate_sigma * s) {
            if (++rejects_ >= 5) {
                bearing_ = z;
                rate_ = 0.0f;
                P_ = kInitialP;
                rejects_ = 0;
            }
            return false;
        }
        rejects_ = 0;

        const float k0 = P_[0][0] / s;
        const float k1 = P_[1][0] / s;
        bearing_ += k0 * innovation;
        rate_ += k1 * innovation;

        const auto p = P_;
        P_[0][0] = (1.0f - k0) * p[0][0];
        P_[0][1] = (1.0f - k0) * p[0][1];
        P_[1][0] = p[1][0] - k1 * p[0][0];
        P_[1][1] = p[1][1] - k1 * p[0][1];
        return true;
    }

    /* Назад у поточну рамку тіла, з випередженням на запізнення приводів. */
    [[nodiscard]] Estimate extrapolate(Seconds lead) const noexcept {
        return {bearing_ + rate_ * lead.count() - body_angle_, rate_};
    }

    [[nodiscard]] constexpr float body_angle() const noexcept { return body_angle_; }
    [[nodiscard]] constexpr bool primed() const noexcept { return primed_; }

private:
    using Matrix2 = std::array<std::array<float, 2>, 2>;
    static constexpr Matrix2 kInitialP{{{0.1f, 0.0f}, {0.0f, 1.0f}}};

    Config cfg_;
    float bearing_{0.0f};
    float rate_{0.0f};
    float body_angle_{0.0f};   /* інтеграл гіроскопа від старту супроводу */
    Matrix2 P_{kInitialP};
    int rejects_{0};
    bool primed_{false};
};

}  // namespace servo
