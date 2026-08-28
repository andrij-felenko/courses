#include <iostream>
#include <cmath>
#include <numbers>
#include <expected>
#include <vector>
#include <string_view>
#include <iomanip>
#include <span>

namespace mechanics::hertz {

enum class ContactGeometryType {
    PointSpherical,
    LineCylindrical
};

struct MaterialProperties {
    double young_modulus{210.0e9};     // Модуль Юнга E, Па
    double poisson_ratio{0.30};        // Коефіцієнт Пуассона nu
    double yield_strength{1900.0e6};   // Границя текучості sigma_y, Па
};

struct GeometryParameters {
    ContactGeometryType type{ContactGeometryType::PointSpherical};
    double radius_1{0.012};            // Радіус першого тіла R1, м
    double radius_2{1.0e12};           // Радіус другого тіла R2, м (1e12 для площини)
    double contact_length{0.0};        // Довжина контакту L для циліндра, м
};

struct ContactAnalysisResult {
    double contact_radius_or_width; // a або b, м
    double indentation_depth;       // delta, м
    double peak_pressure;           // p0, Па
    double mean_pressure;           // p_mean, Па
    double max_shear_stress;        // tau_max, Па
    double critical_depth;          // z_crit, м
    double edge_tensile_stress;     // sigma_tensile на r = a, Па
    double safety_factor;           // Коефіцієнт запасу за Треска
    bool   is_purely_elastic;
};

struct DepthStressEvaluation {
    double depth_z;                 // Глибина z, м
    double normalized_depth;        // z / a
    double sigma_vertical;          // sigma_z, Па
    double sigma_radial;            // sigma_r, Па
    double max_shear;               // tau_max, Па
    double von_mises;               // sigma_vM, Па
};

enum class ContactCalculationError {
    InvalidLoad,
    InvalidGeometry,
    InvalidMaterialProperties
};

[[nodiscard]] constexpr double calculate_reduced_radius(double r1, double r2) noexcept {
    return (r1 * r2) / (r1 + r2);
}

[[nodiscard]] constexpr double calculate_effective_modulus(
    double e1, double nu1, double e2, double nu2) noexcept 
{
    const double inv_e = (1.0 - nu1 * nu1) / e1 + (1.0 - nu2 * nu2) / e2;
    return 1.0 / inv_e;
}

class ContactSolver {
public:
    [[nodiscard]] static std::expected<ContactAnalysisResult, ContactCalculationError> solve(
        const GeometryParameters& geo,
        const MaterialProperties& mat1,
        const MaterialProperties& mat2,
        double normal_load) noexcept 
    {
        if (normal_load <= 0.0) return std::unexpected(ContactCalculationError::InvalidLoad);
        if (geo.radius_1 <= 0.0 || geo.radius_2 <= 0.0) {
            return std::unexpected(ContactCalculationError::InvalidGeometry);
        }
        if (mat1.young_modulus <= 0.0 || mat2.young_modulus <= 0.0 || 
            mat1.yield_strength <= 0.0 || mat2.yield_strength <= 0.0) {
            return std::unexpected(ContactCalculationError::InvalidMaterialProperties);
        }

        const double r_eq = calculate_reduced_radius(geo.radius_1, geo.radius_2);
        const double e_star = calculate_effective_modulus(
            mat1.young_modulus, mat1.poisson_ratio,
            mat2.young_modulus, mat2.poisson_ratio);

        ContactAnalysisResult res{};

        if (geo.type == ContactGeometryType::PointSpherical) {
            res.contact_radius_or_width = std::cbrt((3.0 * normal_load * r_eq) / (4.0 * e_star));
            res.indentation_depth = (res.contact_radius_or_width * res.contact_radius_or_width) / r_eq;
            res.peak_pressure = (3.0 * normal_load) / 
                (2.0 * std::numbers::pi * res.contact_radius_or_width * res.contact_radius_or_width);
            res.mean_pressure = (2.0 / 3.0) * res.peak_pressure;

            res.max_shear_stress = 0.3105 * res.peak_pressure;
            res.critical_depth = 0.481 * res.contact_radius_or_width;
            res.edge_tensile_stress = res.peak_pressure * (1.0 - 2.0 * mat1.poisson_ratio) / 3.0;
        } else {
            if (geo.contact_length <= 0.0) {
                return std::unexpected(ContactCalculationError::InvalidGeometry);
            }

            res.contact_radius_or_width = std::sqrt(
                (4.0 * normal_load * r_eq) / (std::numbers::pi * geo.contact_length * e_star));
            res.indentation_depth = (res.contact_radius_or_width * res.contact_radius_or_width) / r_eq;
            res.peak_pressure = (2.0 * normal_load) / 
                (std::numbers::pi * res.contact_radius_or_width * geo.contact_length);
            res.mean_pressure = (std::numbers::pi / 4.0) * res.peak_pressure;

            res.max_shear_stress = 0.300 * res.peak_pressure;
            res.critical_depth = 0.786 * res.contact_radius_or_width;
            res.edge_tensile_stress = 0.0;
        }

        const double min_yield = std::min(mat1.yield_strength, mat2.yield_strength);
        const double allowable_tau = 0.5 * min_yield;
        res.safety_factor = allowable_tau / res.max_shear_stress;
        res.is_purely_elastic = (res.safety_factor >= 1.0);

        return res;
    }

    [[nodiscard]] static DepthStressEvaluation evaluate_depth_stress(
        const MaterialProperties& mat,
        const ContactAnalysisResult& analysis,
        double depth_z) noexcept 
    {
        const double a = analysis.contact_radius_or_width;
        const double p0 = analysis.peak_pressure;
        const double nu = mat.poisson_ratio;
        const double zeta = depth_z / a;

        const double sz = -p0 / (1.0 + zeta * zeta);
        double sr = 0.0;

        if (zeta < 1.0e-7) {
            sr = -p0 * (1.0 + 2.0 * nu) / 2.0;
        } else {
            sr = -p0 * ((1.0 + nu) * (1.0 - zeta * std::atan(1.0 / zeta)) - 0.5 / (1.0 + zeta * zeta));
        }

        const double tau = 0.5 * std::abs(sz - sr);
        const double vm = std::abs(sz - sr);

        return DepthStressEvaluation{
            .depth_z = depth_z,
            .normalized_depth = zeta,
            .sigma_vertical = sz,
            .sigma_radial = sr,
            .max_shear = tau,
            .von_mises = vm
        };
    }
};

} // namespace mechanics::hertz

int main() {
    using namespace mechanics::hertz;

    const GeometryParameters geometry{
        .type = ContactGeometryType::PointSpherical,
        .radius_1 = 0.012,
        .radius_2 = 1.0e12,
        .contact_length = 0.0
    };

    const MaterialProperties bearing_steel{
        .young_modulus = 210.0e9,
        .poisson_ratio = 0.30,
        .yield_strength = 1900.0e6
    };

    constexpr double load_force = 2500.0; // Н

    const auto solve_result = ContactSolver::solve(geometry, bearing_steel, bearing_steel, load_force);

    if (!solve_result) {
        std::cerr << "Помилка розрахунку параметрів контакту Герца!\n";
        return 1;
    }

    const auto& res = *solve_result;

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "================ КОНТАКТНИЙ АНАЛІЗ ГЕРЦА (C++20) ================\n";
    std::cout << "Нормальне зусилля N:            " << load_force << " Н\n";
    std::cout << "Радіус контактної плями a:      " << res.contact_radius_or_width * 1e3 << " мм\n";
    std::cout << "Пружне зближення delta:         " << res.indentation_depth * 1e6 << " мкм\n";
    std::cout << "Піковий контактний тиск p0:     " << res.peak_pressure * 1e-6 << " МПа\n";
    std::cout << "Середній контактний тиск p_mean:" << res.mean_pressure * 1e-6 << " МПа\n";
    std::cout << "Макс. зсувне напруження tau:    " << res.max_shear_stress * 1e-6 << " МПа\n";
    std::cout << "Глибина залягання піка z_crit:  " << res.critical_depth * 1e3 << " мм\n";
    std::cout << "Крайовий розтяг sigma_tensile:  " << res.edge_tensile_stress * 1e-6 << " МПа\n";
    std::cout << "Запас міцності (Tresca):        " << std::setprecision(2) << res.safety_factor 
              << " (" << (res.is_purely_elastic ? "ПРУЖНИЙ СТАН" : "ПЛАСТИЧНА ТЕКУЧІСТЬ") << ")\n\n";

    std::cout << "--- Епюра напруженого стану по осі глибини z ---\n";
    std::cout << " z/a  | z (мкм) | sigma_z (МПа) | sigma_r (МПа) | tau_max (МПа) | von Mises (МПа)\n";
    std::cout << "------+---------+---------------+---------------+---------------+----------------\n";

    for (int step = 0; step <= 10; ++step) {
        const double z = (step * 0.2) * res.contact_radius_or_width;
        const auto pt = ContactSolver::evaluate_depth_stress(bearing_steel, res, z);
        std::cout << " " << std::setw(4) << std::setprecision(2) << pt.normalized_depth
                  << " | " << std::setw(7) << std::setprecision(1) << (pt.depth_z * 1e6)
                  << " | " << std::setw(13) << (pt.sigma_vertical * 1e-6)
                  << " | " << std::setw(13) << (pt.sigma_radial * 1e-6)
                  << " | " << std::setw(13) << (pt.max_shear * 1e-6)
                  << " | " << std::setw(14) << (pt.von_mises * 1e-6) << "\n";
    }

    return 0;
}
