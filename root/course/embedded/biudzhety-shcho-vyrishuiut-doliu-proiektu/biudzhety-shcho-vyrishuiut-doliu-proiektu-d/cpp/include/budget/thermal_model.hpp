#pragma once

// Теплова модель вузла: T_j = T_a + P * R_th_JA.
//
// Тут, на відміну від цілочислової версії для дешевого ядра, величини
// зберігаються у справжніх одиницях (°C, Вт, °C/Вт): межі рахуються ще на
// етапі компіляції, тож стеля потужності корпусу відома до першого запуску.

#include "budget/flags.hpp"

#include <stdexcept>

namespace budget {

class ThermalModel {
public:
    struct Limits {
        double tj_max_c{125.0};       // максимальна температура переходу
        double warn_margin_c{15.0};   // за скільки до межі піднімати тривогу
        double hysteresis_c{5.0};     // наскільки треба охолонути
        double rth_ja_c_per_w{200.0}; // тепловий опір кристал-середовище
    };

    constexpr explicit ThermalModel(Limits limits) : limits_{limits}
    {
        if (limits_.rth_ja_c_per_w <= 0.0) {
            throw std::invalid_argument{"тепловий опір має бути додатним"};
        }
    }

    [[nodiscard]] static constexpr double junction(double ambient_c,
                                                   double power_w,
                                                   double rth_c_per_w) noexcept
    {
        return ambient_c + power_w * rth_c_per_w;
    }

    // Максимальна потужність, яку вузол розсіє при заданому середовищі.
    [[nodiscard]] constexpr double max_power(double ambient_c) const noexcept
    {
        const double delta = limits_.tj_max_c - ambient_c;
        // Середовище вже гарячіше за допустиму температуру кристала.
        return (delta <= 0.0) ? 0.0 : delta / limits_.rth_ja_c_per_w;
    }

    // Струм, який ще витримає лінійний стабілізатор при перепаді U_in - U_out.
    [[nodiscard]] constexpr double ldo_max_current(double ambient_c,
                                                   double dropout_v) const noexcept
    {
        return (dropout_v <= 0.0) ? 0.0 : max_power(ambient_c) / dropout_v;
    }

    [[nodiscard]] constexpr double warn_threshold_c() const noexcept
    {
        return limits_.tj_max_c - limits_.warn_margin_c;
    }

    Budget sample(double ambient_c, double power_w) noexcept;

    [[nodiscard]] constexpr double ambient_c() const noexcept { return ambient_c_; }
    [[nodiscard]] constexpr double junction_c() const noexcept { return junction_c_; }
    [[nodiscard]] constexpr double peak_c() const noexcept { return peak_c_; }
    [[nodiscard]] constexpr double power_w() const noexcept { return power_w_; }
    [[nodiscard]] constexpr bool throttled() const noexcept { return throttled_; }
    [[nodiscard]] constexpr unsigned trips() const noexcept { return trips_; }
    [[nodiscard]] constexpr const Limits& limits() const noexcept { return limits_; }

private:
    Limits   limits_;
    double   ambient_c_{0.0};
    double   junction_c_{0.0};
    double   peak_c_{-273.15};
    double   power_w_{0.0};
    bool     throttled_{false};
    unsigned trips_{0};
};

} // namespace budget
