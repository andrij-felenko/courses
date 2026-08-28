#include <iostream>
#include <cmath>
#include <numbers>
#include <expected>
#include <string_view>
#include <iomanip>

namespace mechanics::contact {

struct MaterialProperties {
    double young_modulus{210.0e9};     // Па
    double poisson_ratio{0.30};        // безрозмірний
    double yield_strength{1800.0e6};   // Па
};

struct ContactGeometry {
    double radius_1{0.010};            // м (тіло 1)
    double radius_2{1.0e9};            // м (тіло 2, для площини 1e9)
};

struct HertzianAnalysis {
    double contact_radius;     // a, м
    double indentation_depth;  // delta, м
    double peak_pressure;      // p0, Па
    double mean_pressure;      // p_mean, Па
    double max_shear_stress;   // tau_max, Па
    double critical_depth;     // z_crit, м
    double edge_tensile_stress;// sigma_r(a), Па
    double safety_factor;      // n_safety
    bool   is_purely_elastic;
};

enum class ContactError {
    InvalidLoad,
    InvalidGeometry,
    InvalidMaterial
};

[[nodiscard]] constexpr double compute_reduced_radius(double r1, double r2) noexcept {
    return (r1 * r2) / (r1 + r2);
}

[[nodiscard]] constexpr double compute_effective_modulus(
    double e1, double nu1, double e2, double nu2) noexcept {
    const double inv_e = (1.0 - nu1 * nu1) / e1 + (1.0 - nu2 * nu2) / e2;
    return 1.0 / inv_e;
}

[[nodiscard]] std::expected<HertzianAnalysis, ContactError> solve_sphere_contact(
    const ContactGeometry& geo,
    const MaterialProperties& mat1,
    const MaterialProperties& mat2,
    double normal_force) noexcept 
{
    if (normal_force <= 0.0) {
        return std::unexpected(ContactError::InvalidLoad);
    }
    if (geo.radius_1 <= 0.0 || geo.radius_2 <= 0.0) {
        return std::unexpected(ContactError::InvalidGeometry);
    }
    if (mat1.young_modulus <= 0.0 || mat2.young_modulus <= 0.0) {
        return std::unexpected(ContactError::InvalidMaterial);
    }

    const double r_eq = compute_reduced_radius(geo.radius_1, geo.radius_2);
    const double e_star = compute_effective_modulus(
        mat1.young_modulus, mat1.poisson_ratio,
        mat2.young_modulus, mat2.poisson_ratio);

    // Радіус контактної зони a
    const double a = std::cbrt((3.0 * normal_force * r_eq) / (4.0 * e_star));
    const double delta = (a * a) / r_eq;

    // Тиск за Герцом
    const double p0 = (3.0 * normal_force) / (2.0 * std::numbers::pi * a * a);
    const double p_mean = (2.0 / 3.0) * p0;

    // Підповерхневі напруження
    const double tau_max = 0.3105 * p0;
    const double z_crit = 0.481 * a;
    const double sigma_tensile = p0 * (1.0 - 2.0 * mat1.poisson_ratio) / 3.0;

    // Оцінка за міцністю слабшого матеріалу
    const double min_yield = std::min(mat1.yield_strength, mat2.yield_strength);
    const double allowable_tau = 0.5 * min_yield;
    const double safety_factor = allowable_tau / tau_max;

    return HertzianAnalysis{
        .contact_radius = a,
        .indentation_depth = delta,
        .peak_pressure = p0,
        .mean_pressure = p_mean,
        .max_shear_stress = tau_max,
        .critical_depth = z_crit,
        .edge_tensile_stress = sigma_tensile,
        .safety_factor = safety_factor,
        .is_purely_elastic = (safety_factor >= 1.0)
    };
}

} // namespace mechanics::contact

int main() {
    using namespace mechanics::contact;

    const ContactGeometry geometry{.radius_1 = 0.010, .radius_2 = 1.0e9};
    const MaterialProperties steel{.young_modulus = 210.0e9, .poisson_ratio = 0.30, .yield_strength = 1800.0e6};
    constexpr double normal_load = 1500.0; // Н

    const auto result = solve_sphere_contact(geometry, steel, steel, normal_load);

    if (!result) {
        std::cerr << "Помилка обчислення параметрів контакту!\n";
        return 1;
    }

    const auto& res = *result;
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "=== Контактний розрахунок Герца (C++20) ===\n";
    std::cout << "Нормальна сила N:               " << normal_load << " Н\n";
    std::cout << "Радіус контактної плями a:      " << res.contact_radius * 1e3 << " мм\n";
    std::cout << "Пружне зближення delta:         " << res.indentation_depth * 1e6 << " мкм\n";
    std::cout << "Піковий контактний тиск p0:     " << res.peak_pressure * 1e-6 << " МПа\n";
    std::cout << "Середній контактний тиск p_avg: " << res.mean_pressure * 1e-6 << " МПа\n";
    std::cout << "Макс. зсувне напруження tau:    " << res.max_shear_stress * 1e-6 << " МПа\n";
    std::cout << "Глибина залягання піка z_crit:  " << res.critical_depth * 1e3 << " мм\n";
    std::cout << "Крайовий розтяг sigma_r(a):     " << res.edge_tensile_stress * 1e-6 << " МПа\n";
    std::cout << "Коефіцієнт запасу міцності:     " << std::setprecision(2) << res.safety_factor 
              << " (" << (res.is_purely_elastic ? "ПРУЖНИЙ" : "ПЛАСТИЧНИЙ") << ")\n";

    return 0;
}
