// prandtl_solver.hpp - Modern C++20 interface for libprandtl
#ifndef PRANDTL_SOLVER_HPP
#define PRANDTL_SOLVER_HPP

#include <string_view>
#include <expected>
#include <system_error>
#include <cmath>
#include <concepts>

namespace fluid {

enum class FluidType {
    Air,
    Water,
    LiquidSodium,
    Mercury,
    EngineOil,
    Ethanol
};

enum class ErrorCode {
    Success = 0,
    InvalidArgument,
    TemperatureOutOfRange,
    PressureOutOfRange,
    CalculationFailed
};

struct FluidProperties {
    double temperature_k{293.15};
    double pressure_pa{101325.0};
    double density{998.2};
    double dynamic_viscosity{1.002e-3};
    double kin_viscosity{1.004e-6};
    double thermal_cond{0.598};
    double specific_heat{4182.0};
    double thermal_diff{1.43e-7};
    double prandtl_number{7.01};
};

struct BoundaryLayerParams {
    double position_x{0.1};
    double reynolds_x{1e5};
    double pecle_x{7e5};
    double delta_v{0.001};
    double delta_t{0.0005};
    double ratio_delta{2.0};
    double skin_friction_cf{0.002};
    double nusselt_x{100.0};
    double heat_transfer_h{600.0};
};

class PrandtlSolver {
public:
    // Обчислити властивості середовища для заданої температури й тиску
    [[nodiscard]] static std::expected<FluidProperties, ErrorCode> 
    getProperties(FluidType fluid, double temp_k, double press_pa = 101325.0) noexcept {
        if (temp_k <= 0.0 || press_pa <= 0.0) {
            return std::unexpected(ErrorCode::InvalidArgument);
        }

        FluidProperties props{};
        props.temperature_k = temp_k;
        props.pressure_pa = press_pa;

        switch (fluid) {
            case FluidType::Air: {
                if (temp_k < 100.0 || temp_k > 2000.0) return std::unexpected(ErrorCode::TemperatureOutOfRange);
                props.density = press_pa / (287.058 * temp_k);
                props.dynamic_viscosity = 1.716e-5 * std::pow(temp_k / 273.15, 0.7);
                props.kin_viscosity = props.dynamic_viscosity / props.density;
                props.specific_heat = 1005.0;
                props.thermal_cond = 0.0257 * std::pow(temp_k / 273.15, 0.8);
                props.thermal_diff = props.thermal_cond / (props.density * props.specific_heat);
                props.prandtl_number = props.kin_viscosity / props.thermal_diff;
                break;
            }
            case FluidType::Water: {
                if (temp_k < 273.15 || temp_k > 647.0) return std::unexpected(ErrorCode::TemperatureOutOfRange);
                const double tc = temp_k - 273.15;
                props.density = 999.8 + 0.067 * tc - 0.009 * tc * tc;
                props.dynamic_viscosity = 2.414e-5 * std::pow(10.0, 247.8 / (temp_k - 140.0));
                props.kin_viscosity = props.dynamic_viscosity / props.density;
                props.specific_heat = 4182.0;
                props.thermal_cond = 0.56 + 0.0018 * tc;
                props.thermal_diff = props.thermal_cond / (props.density * props.specific_heat);
                props.prandtl_number = props.kin_viscosity / props.thermal_diff;
                break;
            }
            case FluidType::LiquidSodium: {
                if (temp_k < 371.0 || temp_k > 1150.0) return std::unexpected(ErrorCode::TemperatureOutOfRange);
                props.density = 927.0 - 0.23 * (temp_k - 371.15);
                props.dynamic_viscosity = 7.0e-4 * std::exp(600.0 / temp_k);
                props.kin_viscosity = props.dynamic_viscosity / props.density;
                props.specific_heat = 1380.0;
                props.thermal_cond = 86.0 - 0.04 * (temp_k - 371.15);
                props.thermal_diff = props.thermal_cond / (props.density * props.specific_heat);
                props.prandtl_number = props.kin_viscosity / props.thermal_diff;
                break;
            }
            default:
                // Для інших середовищ застосовуємо усереднені апроксимації
                props.prandtl_number = 1.0;
                break;
        }

        return props;
    }

    // Обчислити параметри примежового шару на пластині
    [[nodiscard]] static std::expected<BoundaryLayerParams, ErrorCode>
    calcBoundaryLayer(const FluidProperties& props, double velocity_u, double position_x) noexcept {
        if (velocity_u <= 0.0 || position_x <= 0.0) {
            return std::unexpected(ErrorCode::InvalidArgument);
        }

        BoundaryLayerParams bl{};
        bl.position_x = position_x;
        bl.reynolds_x = (velocity_u * position_x) / props.kin_viscosity;
        bl.pecle_x = bl.reynolds_x * props.prandtl_number;

        bl.delta_v = 5.0 * position_x / std::sqrt(bl.reynolds_x);
        
        if (props.prandtl_number >= 0.6) {
            bl.ratio_delta = std::pow(props.prandtl_number, 1.0 / 3.0);
            bl.nusselt_x = 0.332 * std::sqrt(bl.reynolds_x) * std::pow(props.prandtl_number, 1.0 / 3.0);
        } else {
            bl.ratio_delta = std::sqrt(props.prandtl_number);
            bl.nusselt_x = 0.564 * std::sqrt(bl.pecle_x);
        }

        bl.delta_t = bl.delta_v / bl.ratio_delta;
        bl.skin_friction_cf = 0.664 / std::sqrt(bl.reynolds_x);
        bl.heat_transfer_h = bl.nusselt_x * props.thermal_cond / position_x;

        return bl;
    }
};

} // namespace fluid

#endif // PRANDTL_SOLVER_HPP
