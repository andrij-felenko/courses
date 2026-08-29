#pragma once

// Нагляд за шиною живлення та розрахунок просідання на сплеску струму.
//
// Середній струм нічого не гарантує: старт передавача рве з шини сотні
// міліампер за одиниці мікросекунд. Оцінка просідання рахується ще до
// розведення плати, а монітор під час роботи тримає найгірший відлік.

#include "budget/flags.hpp"

#include <chrono>
#include <limits>
#include <stdexcept>

namespace budget {

class RailMonitor {
public:
    struct Limits {
        double nominal_v{3.3};
        double warn_v{3.0};  // запас до BOR вичерпується
        double bor_v{2.9};   // поріг скидання за зниження напруги
    };

    constexpr explicit RailMonitor(Limits limits) : limits_{limits}
    {
        if (!(limits_.bor_v < limits_.warn_v && limits_.warn_v <= limits_.nominal_v)) {
            throw std::invalid_argument{"пороги шини мають зростати: BOR < warn <= nominal"};
        }
        last_v_ = limits_.nominal_v;
        min_v_  = limits_.nominal_v;
    }

    Budget sample(double volts) noexcept;

    // dV = I_peak * ESR + I_peak * dt / C_bulk
    [[nodiscard]] static constexpr double estimated_droop_v(
        double peak_a, double esr_ohm, double bulk_f,
        std::chrono::microseconds burst) noexcept
    {
        if (bulk_f <= 0.0) {
            // Без буферної ємності просідання нічим не обмежене.
            return std::numeric_limits<double>::infinity();
        }
        const double burst_s = std::chrono::duration<double>{burst}.count();
        return peak_a * esr_ohm + peak_a * burst_s / bulk_f;
    }

    [[nodiscard]] constexpr double last_v() const noexcept { return last_v_; }
    [[nodiscard]] constexpr double min_v() const noexcept { return min_v_; }
    [[nodiscard]] constexpr double headroom_v() const noexcept
    {
        return min_v_ - limits_.bor_v;
    }
    [[nodiscard]] constexpr unsigned sags() const noexcept { return sags_; }
    [[nodiscard]] constexpr unsigned brownouts() const noexcept { return brownouts_; }
    [[nodiscard]] constexpr const Limits& limits() const noexcept { return limits_; }

private:
    Limits   limits_;
    double   last_v_{0.0};
    double   min_v_{0.0};
    unsigned samples_{0};
    unsigned sags_{0};
    unsigned brownouts_{0};
};

} // namespace budget
