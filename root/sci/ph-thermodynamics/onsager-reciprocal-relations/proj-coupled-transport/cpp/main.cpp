#include <iostream>
#include <iomanip>
#include <cmath>
#include <expected>
#include <string_view>

struct ThermoMaterial {
    double sigma;   // Питома електропровідність (См/м)
    double kappa;   // Питома теплопровідність (Вт/(м·К))
    double seebeck; // Коефіцієнт Зеебека (В/К)
};

class OnsagerCoupledSolver {
public:
    struct Matrix {
        double L_qq;
        double L_qe;
        double L_eq;
        double L_ee;

        [[nodiscard]] constexpr bool is_thermodynamically_stable() const noexcept {
            const double det = L_qq * L_ee - L_qe * L_eq;
            return (L_qq > 0.0) && (L_ee > 0.0) && (det >= 0.0);
        }
    };

    struct SimulationResult {
        double heat_flux;           // Потік тепла J_q (Вт/м²)
        double current_density;     // Густина струму J_e (А/м²)
        double open_circuit_voltage;// Напруга холостого ходу (В)
        double peltier_coefficient; // Коефіцієнт Пельтьє (В)
        double electrical_power_w;  // Потужність на навантаженні (Вт)
        double efficiency_percent;  // ККД (%)
        double zt_figure_of_merit;  // Безрозмірна добротність ZT
    };

    enum class SimulationError {
        InvalidGeometry,
        InvalidTemperature,
        UnstableMatrix
    };

    static constexpr Matrix build_onsager_matrix(const ThermoMaterial& mat, double temp_k) noexcept {
        const double L_ee = mat.sigma * temp_k;
        const double L_eq = mat.seebeck * mat.sigma * temp_k * temp_k;
        // Симетрія Онсагера: L_qe = L_eq
        const double L_qe = L_eq; 
        const double L_qq = (mat.kappa + mat.seebeck * mat.seebeck * mat.sigma * temp_k) * temp_k * temp_k;

        return Matrix{ .L_qq = L_qq, .L_qe = L_qe, .L_eq = L_eq, .L_ee = L_ee };
    }

    static std::expected<SimulationResult, SimulationError> simulate(
        const ThermoMaterial& mat,
        double t_hot, double t_cold,
        double length, double area,
        double load_resistance) noexcept
    {
        if (length <= 0.0 || area <= 0.0) return std::unexpected(SimulationError::InvalidGeometry);
        if (t_hot <= t_cold) return std::unexpected(SimulationError::InvalidTemperature);

        const double t_avg = 0.5 * (t_hot + t_cold);
        const Matrix L = build_onsager_matrix(mat, t_avg);

        if (!L.is_thermodynamically_stable()) {
            return std::unexpected(SimulationError::UnstableMatrix);
        }

        const double zt = (mat.seebeck * mat.seebeck * mat.sigma / mat.kappa) * t_avg;
        const double X_q = -(t_hot - t_cold) / (t_avg * t_avg * length);
        const double open_circuit_v = mat.seebeck * (t_hot - t_cold);
        const double peltier_coeff = L.L_qe / L.L_ee;

        const double internal_r = length / (mat.sigma * area);
        const double total_current = open_circuit_v / (internal_r + load_resistance);
        const double current_density = total_current / area;

        const double grad_phi = -current_density / mat.sigma;
        const double X_e = -grad_phi / t_avg;

        const double j_q = L.L_qq * X_q + L.L_qe * X_e;
        const double j_e = L.L_eq * X_q + L.L_ee * X_e;

        const double electrical_power = total_current * total_current * load_resistance;
        const double total_thermal_input = j_q * area;
        const double efficiency = (electrical_power / total_thermal_input) * 100.0;

        return SimulationResult{
            .heat_flux = j_q,
            .current_density = j_e,
            .open_circuit_voltage = open_circuit_v,
            .peltier_coefficient = peltier_coeff,
            .electrical_power_w = electrical_power,
            .efficiency_percent = efficiency,
            .zt_figure_of_merit = zt
        };
    }
};

int main() {
    constexpr ThermoMaterial bi2te3{
        .sigma = 100000.0,
        .kappa = 1.5,
        .seebeck = 200e-6
    };

    constexpr double t_hot = 373.15;
    constexpr double t_cold = 293.15;
    constexpr double length = 0.005;
    constexpr double area = 1e-6;
    constexpr double load_r = 0.25;

    auto result = OnsagerCoupledSolver::simulate(bi2te3, t_hot, t_cold, length, area, load_r);

    if (result) {
        std::cout << std::fixed << std::setprecision(4);
        std::cout << "=== Симуляція термоелектричного елемента (C++) ===\n";
        std::cout << "Добротність ZT:        " << result->zt_figure_of_merit << "\n";
        std::cout << "Термо-ЕРС (Зеебек):    " << result->open_circuit_voltage << " В\n";
        std::cout << "Коефіцієнт Пельтьє:    " << result->peltier_coefficient << " В\n";
        std::cout << "Густина тепла J_q:     " << result->heat_flux << " Вт/м²\n";
        std::cout << "Густина струму J_e:    " << result->current_density << " А/м²\n";
        std::cout << "Потужність P:          " << std::setprecision(6) << result->electrical_power_w << " Вт\n";
        std::cout << "ККД перетворення:      " << std::setprecision(2) << result->efficiency_percent << " %\n";
    } else {
        std::cerr << "Помилка симуляції термодинамічного переносу!\n";
    }

    return 0;
}
