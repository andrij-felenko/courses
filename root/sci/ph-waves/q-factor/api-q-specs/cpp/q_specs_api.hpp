// q_specs_api.hpp — C++20 Специфікація API добротності
#pragma once

#include <variant>
#include <expected>
#include <string_view>
#include <cmath>
#include <numbers>

namespace physics::oscillations::api {

enum class QDomain {
    Mechanical,
    ElectricalSeries,
    ElectricalParallel,
    Acoustic,
    Optical
};

enum class QError {
    InvalidParameter,
    Overdamped,
    NumericalOverflow
};

struct MechanicalParams {
    double mass_kg{0.0};
    double stiffness_nm{0.0};
    double damping_c{0.0};
};

struct ElectricalParams {
    double resistance_ohm{0.0};
    double inductance_henry{0.0};
    double capacitance_farad{0.0};
};

struct EnergyParams {
    double w_stored_joules{0.0};
    double w_lost_per_cycle{0.0};
    double f0_hz{0.0};
};

struct QResult {
    double q_factor{0.0};
    double f0_hz{0.0};
    double bandwidth_3db_hz{0.0};
    double damping_ratio_zeta{0.0};
    double decay_time_tau_sec{0.0};
    QDomain domain{QDomain::Mechanical};
};

class QCalculator {
public:
    [[nodiscard]] static std::expected<QResult, QError> calculate(const MechanicalParams& p) noexcept {
        if (p.mass_kg <= 0.0 || p.stiffness_nm <= 0.0 || p.damping_c <= 0.0) {
            return std::unexpected(QError::InvalidParameter);
        }

        double omega0 = std::sqrt(p.stiffness_nm / p.mass_kg);
        double f0 = omega0 / (2.0 * std::numbers::pi);
        double q = (p.mass_kg * omega0) / p.damping_c;
        double zeta = 1.0 / (2.0 * q);

        if (q < 0.5) {
            return std::unexpected(QError::Overdamped);
        }

        return QResult{
            .q_factor = q,
            .f0_hz = f0,
            .bandwidth_3db_hz = f0 / q,
            .damping_ratio_zeta = zeta,
            .decay_time_tau_sec = q / (std::numbers::pi * f0),
            .domain = QDomain::Mechanical
        };
    }

    [[nodiscard]] static std::expected<QResult, QError> calculateSeries(const ElectricalParams& p) noexcept {
        if (p.resistance_ohm <= 0.0 || p.inductance_henry <= 0.0 || p.capacitance_farad <= 0.0) {
            return std::unexpected(QError::InvalidParameter);
        }

        double omega0 = 1.0 / std::sqrt(p.inductance_henry * p.capacitance_farad);
        double f0 = omega0 / (2.0 * std::numbers::pi);
        double q = (omega0 * p.inductance_henry) / p.resistance_ohm;
        double zeta = 1.0 / (2.0 * q);

        if (q < 0.5) {
            return std::unexpected(QError::Overdamped);
        }

        return QResult{
            .q_factor = q,
            .f0_hz = f0,
            .bandwidth_3db_hz = f0 / q,
            .damping_ratio_zeta = zeta,
            .decay_time_tau_sec = q / (std::numbers::pi * f0),
            .domain = QDomain::ElectricalSeries
        };
    }
};

} // namespace physics::oscillations::api
