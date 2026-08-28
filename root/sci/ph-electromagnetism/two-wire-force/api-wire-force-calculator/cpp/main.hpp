#ifndef WIREFORCE_HPP
#define WIREFORCE_HPP

#include <expected>
#include <string_view>
#include <span>
#include "wireforce.h"

namespace wireforce {

enum class Error : int32_t {
    NullPointer         = WF_ERR_NULL_POINTER,
    InvalidCurrent      = WF_ERR_INVALID_CURRENT,
    InvalidDistance     = WF_ERR_INVALID_DISTANCE,
    InvalidSpan         = WF_ERR_INVALID_SPAN,
    InvalidGeometry     = WF_ERR_INVALID_GEOMETRY,
    InvalidShockFactor  = WF_ERR_INVALID_SHOCK_FACTOR,
    StressExceeded      = WF_ERR_STRESS_EXCEEDED,
    InsulatorOverload   = WF_ERR_INSULATOR_OVERLOAD
};

[[nodiscard]] constexpr std::string_view format_error(Error err) noexcept {
    return wf_status_to_string(static_cast<wf_status_t>(err));
}

class ForceCalculator {
public:
    [[nodiscard]] static std::expected<double, Error>
    parallel_wire_force(double i1_amp, double i2_amp, 
                        double distance_m, double length_m) noexcept 
    {
        double force = 0.0;
        const auto status = wf_calculate_parallel_force(
            i1_amp, i2_amp, distance_m, length_m, &force
        );
        if (status == WF_SUCCESS) {
            return force;
        }
        return std::unexpected(static_cast<Error>(status));
    }

    [[nodiscard]] static std::expected<wf_calc_result_t, Error>
    analyze_busbar(const wf_wire_geometry_t& geo,
                   const wf_sc_params_t& sc,
                   const wf_material_limits_t& mat) noexcept 
    {
        wf_calc_result_t result{};
        const auto status = wf_calculate_busbar_system(&geo, &sc, &mat, &result);
        if (status == WF_SUCCESS) {
            return result;
        }
        return std::unexpected(static_cast<Error>(status));
    }
};

} // namespace wireforce

#endif // WIREFORCE_HPP
