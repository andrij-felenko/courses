//
// charge_relaxation_api.hpp — C++20 API розрахунку параметрів релаксації
//

#ifndef CHARGE_RELAXATION_API_HPP
#define CHARGE_RELAXATION_API_HPP

#include <cmath>
#include <expected>
#include <system_error>
#include <string_view>

namespace physics::electromagnetism {

inline constexpr double EPSILON_0 = 8.854187817e-12;

enum class RelaxationError {
    InvalidParam,
    ZeroConductivity,
    NegativeThickness
};

struct Material {
    double relative_permittivity{1.0};
    double conductivity_sm_per_m{0.0};
};

struct RelaxationMetrics {
    double tau_maxwell_seconds;
    double half_life_seconds;
    double decay_99_percent_seconds;
};

struct MaxwellWagnerMetrics {
    double tau_mw_seconds;
    double interface_charge_density_c_per_m2;
};

class ChargeRelaxationCalculator {
public:
    [[nodiscard]] static std::expected<RelaxationMetrics, RelaxationError>
    calculate_relaxation(const Material& mat) noexcept {
        if (mat.conductivity_sm_per_m <= 0.0 || mat.relative_permittivity <= 0.0) {
            return std::unexpected(RelaxationError::ZeroConductivity);
        }

        const double eps = mat.relative_permittivity * EPSILON_0;
        const double tau = eps / mat.conductivity_sm_per_m;
        const double half_life = tau * std::log(2.0);
        const double decay_99 = tau * std::log(100.0);

        return RelaxationMetrics{
            .tau_maxwell_seconds = tau,
            .half_life_seconds = half_life,
            .decay_99_percent_seconds = decay_99
        };
    }

    [[nodiscard]] static std::expected<double, RelaxationError>
    calculate_esd_decay_time(const Material& mat, double v_initial, double v_target) noexcept {
        if (v_initial <= 0.0 || v_target <= 0.0 || v_target >= v_initial) {
            return std::unexpected(RelaxationError::InvalidParam);
        }

        auto res = calculate_relaxation(mat);
        if (!res) return std::unexpected(res.error());

        return res->tau_maxwell_seconds * std::log(v_initial / v_target);
    }

    [[nodiscard]] static std::expected<MaxwellWagnerMetrics, RelaxationError>
    calculate_maxwell_wagner(const Material& mat1, double d1,
                             const Material& mat2, double d2,
                             double voltage) noexcept {
        if (d1 <= 0.0 || d2 <= 0.0) {
            return std::unexpected(RelaxationError::NegativeThickness);
        }
        if (mat1.conductivity_sm_per_m < 0.0 || mat2.conductivity_sm_per_m < 0.0) {
            return std::unexpected(RelaxationError::ZeroConductivity);
        }

        const double eps1 = mat1.relative_permittivity * EPSILON_0;
        const double eps2 = mat2.relative_permittivity * EPSILON_0;

        const double denom_cond = mat1.conductivity_sm_per_m * d2 + mat2.conductivity_sm_per_m * d1;
        if (denom_cond <= 0.0) {
            return std::unexpected(RelaxationError::ZeroConductivity);
        }

        const double tau_mw = (eps1 * d2 + eps2 * d1) / denom_cond;
        const double sigma_f = voltage * (mat1.conductivity_sm_per_m * eps2 - mat2.conductivity_sm_per_m * eps1) / denom_cond;

        return MaxwellWagnerMetrics{
            .tau_mw_seconds = tau_mw,
            .interface_charge_density_c_per_m2 = sigma_f
        };
    }
};

} // namespace physics::electromagnetism

#endif // CHARGE_RELAXATION_API_HPP
