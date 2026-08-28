#include <iostream>
#include <cmath>
#include <vector>
#include <numbers>
#include <expected>
#include <optional>
#include <span>
#include <iomanip>

namespace hertz {

struct Material {
    double E;      // Модуль Юнга (Па)
    double nu;     // Коефіцієнт Пуассона
};

enum class ContactError {
    InvalidForce,
    InvalidGeometry,
    InvalidMaterial
};

struct SphereResult {
    double R_star;   // Зведений радіус кривини (м)
    double E_star;   // Зведений модуль пружності (Па)
    double a;        // Радіус плями контакту (м)
    double delta;    // Глибина втискання/зближення (м)
    double p0;       // Піковий контактний тиск (Па)
    double p_mean;   // Середній контактний тиск (Па)
    double area;     // Площа контакту (м²)
    double z_peak;   // Глибина піку зсувного напруження (м)
    double tau_max;  // Максимальне зсувне напруження (Па)
};

struct StressPoint {
    double z;          // Глибина під поверхнею (м)
    double z_over_a;   // Відносна глибина z / a
    double sigma_z;    // Осьове стискальне напруження (Па)
    double sigma_x;    // Радіальне стискальне напруження (Па)
    double tau_max;    // Максимальне зсувне напруження (Па)
};

class HertzSolver {
public:
    [[nodiscard]] static constexpr double calc_r_star(double R1, double R2) noexcept {
        return (R1 > 0.0 && R2 > 0.0) ? (R1 * R2) / (R1 + R2) : 0.0;
    }

    [[nodiscard]] static constexpr double calc_e_star(const Material& m1, const Material& m2) noexcept {
        if (m1.E <= 0.0 || m2.E <= 0.0) return 0.0;
        const double inv1 = (1.0 - m1.nu * m1.nu) / m1.E;
        const double inv2 = (1.0 - m2.nu * m2.nu) / m2.E;
        return 1.0 / (inv1 + inv2);
    }

    [[nodiscard]] static std::expected<SphereResult, ContactError> 
    solve_sphere(double F, double R1, double R2, const Material& m1, const Material& m2) noexcept {
        if (F <= 0.0) return std::unexpected(ContactError::InvalidForce);

        const double R_star = calc_r_star(R1, R2);
        const double E_star = calc_e_star(m1, m2);
        if (R_star <= 0.0 || E_star <= 0.0) return std::unexpected(ContactError::InvalidGeometry);

        SphereResult res{};
        res.R_star = R_star;
        res.E_star = E_star;
        res.a = std::cbrt((3.0 * F * R_star) / (4.0 * E_star));
        res.delta = (res.a * res.a) / R_star;
        res.area = std::numbers::pi * res.a * res.a;
        res.p0 = (3.0 * F) / (2.0 * res.area);
        res.p_mean = F / res.area;
        res.z_peak = 0.481 * res.a;
        res.tau_max = 0.310 * res.p0;

        return res;
    }

    [[nodiscard]] static std::vector<StressPoint> 
    calc_stress_profile(const SphereResult& sph, double z_max, std::size_t steps) {
        std::vector<StressPoint> profile;
        if (steps == 0 || z_max <= 0.0) return profile;

        profile.reserve(steps + 1);
        const double dz = z_max / static_cast<double>(steps);
        constexpr double nu = 0.30;

        for (std::size_t i = 0; i <= steps; ++i) {
            const double z = static_cast<double>(i) * dz;
            const double za = (sph.a > 0.0) ? (z / sph.a) : 0.0;

            StressPoint pt{};
            pt.z = z;
            pt.z_over_a = za;

            if (za < 1e-6) {
                pt.sigma_z = -sph.p0;
                pt.sigma_x = -sph.p0 * (0.5 + nu);
            } else {
                pt.sigma_z = -sph.p0 / (1.0 + za * za);
                pt.sigma_x = -sph.p0 * ((1.0 + nu) * (1.0 - za * std::atan(1.0 / za)) - 0.5 / (1.0 + za * za));
            }

            pt.tau_max = 0.5 * std::abs(pt.sigma_z - pt.sigma_x);
            profile.push_back(pt);
        }

        return profile;
    }
};

} // namespace hertz

int main() {
    using namespace hertz;

    constexpr Material steel{ .E = 210e9, .nu = 0.30 };
    constexpr double F = 5000.0;   // 5 кН
    constexpr double R1 = 0.010;   // 10 мм
    constexpr double R2 = 1.0e9;   // Площина

    auto result = HertzSolver::solve_sphere(F, R1, R2, steel, steel);

    if (result) {
        const auto& res = result.value();
        std::cout << "=== [C++] Розрахунок контакту Герца ===\n"
                  << std::fixed << std::setprecision(4)
                  << "Радіус плями a:    " << res.a * 1e3 << " мм\n"
                  << "Глибина втискання: " << res.delta * 1e6 << " мкм\n"
                  << "Піковий тиск p0:   " << res.p0 / 1e6 << " МПа\n"
                  << "Середній тиск:     " << res.p_mean / 1e6 << " МПа\n"
                  << "Пік зсуву z_пік:   " << res.z_peak * 1e3 << " мм\n"
                  << "Макс. зсув tau:    " << res.tau_max / 1e6 << " МПа\n";

        const auto profile = HertzSolver::calc_stress_profile(res, 2.0 * res.a, 5);
        std::cout << "\n--- [C++] Профіль напружень по глибині ---\n"
                  << " z/a   |  z (мм) |  sigma_z (МПа) |  tau_max (МПа)\n"
                  << "-------+---------+----------------+----------------\n";
        for (const auto& pt : profile) {
            std::cout << " " << std::setw(4) << std::setprecision(2) << pt.z_over_a << "  |  "
                      << std::setw(6) << std::setprecision(4) << pt.z * 1e3 << " |    "
                      << std::setw(10) << std::setprecision(2) << pt.sigma_z / 1e6 << "  |    "
                      << std::setw(10) << std::setprecision(2) << pt.tau_max / 1e6 << "\n";
        }
    } else {
        std::cerr << "Помилка розрахунку контактної взаємодії!\n";
    }

    return 0;
}
