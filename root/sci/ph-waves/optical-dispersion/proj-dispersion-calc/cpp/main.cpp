#include <iostream>
#include <string>
#include <string_view>
#include <cmath>
#include <iomanip>
#include <array>
#include <vector>

constexpr double C_VACUUM = 299792458.0; // Швидкість світла у вакуумі (м/с)

struct GlassCoefficients {
    std::array<double, 3> B{};
    std::array<double, 3> C{};
};

class SellmeierSolver {
private:
    std::string m_name;
    GlassCoefficients m_coeffs;

public:
    SellmeierSolver(std::string name, GlassCoefficients coeffs)
        : m_name(std::move(name)), m_coeffs(coeffs) {}

    [[nodiscard]] std::string_view name() const noexcept { return m_name; }

    // Показник заломлення n(lambda)
    [[nodiscard]] double n(double lambda_um) const noexcept {
        const double l2 = lambda_um * lambda_um;
        const double n2 = 1.0 + (m_coeffs.B[0] * l2) / (l2 - m_coeffs.C[0])
                              + (m_coeffs.B[1] * l2) / (l2 - m_coeffs.C[1])
                              + (m_coeffs.B[2] * l2) / (l2 - m_coeffs.C[2]);
        return std::sqrt(n2);
    }

    // Перша похідна dn / dlambda
    [[nodiscard]] double dn_dlambda(double lambda_um, double h = 1e-4) const noexcept {
        return (n(lambda_um + h) - n(lambda_um - h)) / (2.0 * h);
    }

    // Друга похідна d^2n / dlambda^2
    [[nodiscard]] double d2n_dlambda2(double lambda_um, double h = 1e-4) const noexcept {
        return (n(lambda_um + h) - 2.0 * n(lambda_um) + n(lambda_um - h)) / (h * h);
    }

    // Груповий показник заломлення n_g = n - lambda * (dn/dlambda)
    [[nodiscard]] double group_index(double lambda_um) const noexcept {
        return n(lambda_um) - lambda_um * dn_dlambda(lambda_um);
    }

    // Число Аббе V_d
    [[nodiscard]] double abbe_number() const noexcept {
        const double n_d = n(0.587562);
        const double n_F = n(0.486133);
        const double n_C = n(0.656273);
        return (n_d - 1.0) / (n_F - n_C);
    }

    // Матеріальна дисперсія D у пс / (нм * км)
    [[nodiscard]] double material_dispersion(double lambda_um) const noexcept {
        const double d2n = d2n_dlambda2(lambda_um);
        const double lambda_m = lambda_um * 1e-6;
        const double d2n_m2 = d2n * 1e12;
        const double D_s_m2 = -(lambda_m / C_VACUUM) * d2n_m2;
        return D_s_m2 * 1e6;
    }

    // Часове розширення імпульсу delta_t (пікосекунди)
    [[nodiscard]] double pulse_broadening_ps(double lambda_um, double delta_lambda_nm, double length_km) const noexcept {
        return std::abs(material_dispersion(lambda_um)) * delta_lambda_nm * length_km;
    }
};

int main() {
    const SellmeierSolver fused_silica(
        "Fused Silica (Кварцеве скло)",
        GlassCoefficients{
            {0.6961663, 0.4079426, 0.8974794},
            {0.004679148, 0.01351206, 97.93400254}
        }
    );

    const std::vector<double> wavelengths_um = {0.85, 1.31, 1.55}; // стандартні телеком-вікна
    const double delta_lambda_nm = 1.5; // ширина лазера 1.5 нм
    const double fiber_length_km = 20.0; // лінія 20 км

    std::cout << std::fixed << std::setprecision(5);
    std::cout << "Оптичний аналіз середовища: " << fused_silica.name() << "\n";
    std::cout << "Число Аббе V_d: " << fused_silica.abbe_number() << "\n\n";

    std::cout << "Довжина хвилі |   n(lambda)   |     n_g       | D [пс/(нм*км)] | Розширення (20 км)\n";
    std::cout << "--------------|---------------|---------------|----------------|-------------------\n";

    for (const double wave : wavelengths_um) {
        const double n_val = fused_silica.n(wave);
        const double ng_val = fused_silica.group_index(wave);
        const double D_val = fused_silica.material_dispersion(wave);
        const double dt_ps = fused_silica.pulse_broadening_ps(wave, delta_lambda_nm, fiber_length_km);

        std::cout << std::setw(9) << wave << " мкм | "
                  << std::setw(13) << n_val << " | "
                  << std::setw(13) << ng_val << " | "
                  << std::setw(14) << D_val << " | "
                  << std::setw(12) << dt_ps << " пс\n";
    }

    return 0;
}
