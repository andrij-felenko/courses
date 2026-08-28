// 
// hertz_contact.hpp — C++20 API для розрахунку контакту Герца
//

#ifndef HERTZ_CONTACT_HPP
#define HERTZ_CONTACT_HPP

#include <cmath>
#include <vector>
#include <expected>
#include <span>
#include <numbers>
#include <system_error>

namespace hertz {

/* Фізичні властивості матеріалу */
struct Material {
    double E;    // Модуль Юнга (Па)
    double nu;   // Коефіцієнт Пуассона
};

/* Коди помилок виконання */
enum class ErrorCode {
    InvalidForce = 1,
    InvalidGeometry,
    InvalidMaterial,
    NullBuffer
};

/* Клас помилки для std::expected */
class ContactErrorCategory : public std::error_category {
public:
    [[nodiscard]] const char* name() const noexcept override { return "hertz_contact"; }
    [[nodiscard]] std::string message(int ev) const override {
        switch (static_cast<ErrorCode>(ev)) {
            case ErrorCode::InvalidForce: return "Сила стискання має бути строго більшою за нуль";
            case ErrorCode::InvalidGeometry: return "Некоректний або від'ємний радіус кривини";
            case ErrorCode::InvalidMaterial: return "Модуль пружності має бути > 0, коефіцієнт Пуассона у межах [0, 0.5)";
            case ErrorCode::NullBuffer: return "Передано нульовий буфер для результатів";
            default: return "Невідома помилка контактної взаємодії";
        }
    }
};

[[nodiscard]] inline const std::error_category& error_category() noexcept {
    static ContactErrorCategory cat;
    return cat;
}

[[nodiscard]] inline std::error_code make_error_code(ErrorCode e) noexcept {
    return {static_cast<int>(e), error_category()};
}

/* Результати сферичного контакту */
struct SphereResult {
    double R_star;   // Зведений радіус кривини (м)
    double E_star;   // Зведений модуль пружності (Па)
    double a;        // Радіус плями контакту (м)
    double delta;    // Глибина втискання (м)
    double p0;       // Піковий тиск (Па)
    double p_mean;   // Середній тиск (Па)
    double area;     // Площа контакту (м²)
    double z_peak;   // Глибина піку зсуву (м)
    double tau_max;  // Максимальний зсув (Па)
};

/* Результати циліндричного контакту */
struct CylinderResult {
    double R_star;
    double E_star;
    double b;
    double delta;
    double p0;
    double p_mean;   
    double area;     
};

/* Точка профілю напружень */
struct StressPoint {
    double z;          // Глибина (м)
    double z_over_a;   // Безрозмірна глибина z / a
    double sigma_z;    // Осьове напруження (Па)
    double sigma_x;    // Радіальне напруження (Па)
    double tau_max;    // Максимальний зсув (Па)
};

/* Інтерфейсний клас солвера контакту Герца */
class ContactSolver {
public:
    ContactSolver() = delete;

    [[nodiscard]] static constexpr double calc_r_star(double R1, double R2) noexcept {
        return (R1 > 0.0 && R2 > 0.0) ? (R1 * R2) / (R1 + R2) : 0.0;
    }

    [[nodiscard]] static constexpr double calc_e_star(const Material& m1, const Material& m2) noexcept {
        if (m1.E <= 0.0 || m2.E <= 0.0 || m1.nu < 0.0 || m1.nu >= 0.5 || m2.nu < 0.0 || m2.nu >= 0.5) {
            return 0.0;
        }
        const double inv1 = (1.0 - m1.nu * m1.nu) / m1.E;
        const double inv2 = (1.0 - m2.nu * m2.nu) / m2.E;
        return 1.0 / (inv1 + inv2);
    }

    /* Розв'язок для сферичного контакту */
    [[nodiscard]] static std::expected<SphereResult, std::error_code>
    solve_sphere(double F, double R1, double R2, const Material& m1, const Material& m2) noexcept {
        if (F <= 0.0) return std::unexpected(make_error_code(ErrorCode::InvalidForce));

        const double R_star = calc_r_star(R1, R2);
        const double E_star = calc_e_star(m1, m2);
        if (R_star <= 0.0) return std::unexpected(make_error_code(ErrorCode::InvalidGeometry));
        if (E_star <= 0.0) return std::unexpected(make_error_code(ErrorCode::InvalidMaterial));

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

    /* Розв'язок для циліндричного контакту */
    [[nodiscard]] static std::expected<CylinderResult, std::error_code>
    solve_cylinder(double F, double L, double R1, double R2, const Material& m1, const Material& m2) noexcept {
        if (F <= 0.0 || L <= 0.0) return std::unexpected(make_error_code(ErrorCode::InvalidForce));

        const double R_star = calc_r_star(R1, R2);
        const double E_star = calc_e_star(m1, m2);
        if (R_star <= 0.0) return std::unexpected(make_error_code(ErrorCode::InvalidGeometry));
        if (E_star <= 0.0) return std::unexpected(make_error_code(ErrorCode::InvalidMaterial));

        CylinderResult res{};
        res.R_star = R_star;
        res.E_star = E_star;
        res.b = std::sqrt((4.0 * F * R_star) / (std::numbers::pi * L * E_star));
        res.delta = (2.0 * F / (std::numbers::pi * L * E_star)) * 
                     (1.0 + std::log((std::numbers::pi * L * L * E_star) / (F * R_star)));
        res.p0 = std::sqrt((F * E_star) / (std::numbers::pi * L * R_star));
        res.area = 2.0 * res.b * L;
        res.p_mean = F / res.area;

        return res;
    }

    /* Розрахунок вектора профілю напружень */
    [[nodiscard]] static std::vector<StressPoint>
    calc_stress_profile(const SphereResult& sph, double z_max, std::size_t steps) {
        std::vector<StressPoint> vec;
        if (steps == 0 || z_max <= 0.0) return vec;

        vec.reserve(steps + 1);
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
            vec.push_back(pt);
        }

        return vec;
    }
};

} // namespace hertz

#endif // HERTZ_CONTACT_HPP
