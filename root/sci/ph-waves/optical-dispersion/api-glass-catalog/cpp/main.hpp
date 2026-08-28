#ifndef GLASS_CATALOG_HPP
#define GLASS_CATALOG_HPP

#include <string>
#include <string_view>
#include <array>
#include <vector>
#include <optional>
#include <cmath>
#include <stdexcept>

namespace optics {

enum class SpectralLine {
    i_Mercury,
    h_Mercury,
    g_Mercury,
    F_Hydrogen,
    e_Mercury,
    d_Helium,
    C_Hydrogen,
    r_Helium,
    s_Cesium,
    t_Mercury
};

constexpr double get_wavelength_um(SpectralLine line) noexcept {
    switch (line) {
        case SpectralLine::i_Mercury:  return 0.365015;
        case SpectralLine::h_Mercury:  return 0.404656;
        case SpectralLine::g_Mercury:  return 0.435834;
        case SpectralLine::F_Hydrogen: return 0.486133;
        case SpectralLine::e_Mercury:  return 0.546074;
        case SpectralLine::d_Helium:   return 0.587562;
        case SpectralLine::C_Hydrogen: return 0.656273;
        case SpectralLine::r_Helium:   return 0.706519;
        case SpectralLine::s_Cesium:   return 0.852110;
        case SpectralLine::t_Mercury:  return 1.013980;
    }
    return 0.587562;
}

struct SellmeierParams {
    std::array<double, 3> B{}; // Амплітудні безрозмірні коефіцієнти
    std::array<double, 3> C{}; // Квадрати резонансних хвиль (мкм²)
};

struct ThermoOpticParams {
    double D0{0.0};
    double D1{0.0};
    double D2{0.0};
    double E0{0.0};
    double E1{0.0};
};

class OpticalMaterial {
private:
    std::string m_name;
    std::string m_supplier;
    SellmeierParams m_sellmeier;
    ThermoOpticParams m_thermo;
    double m_n_d_catalog{1.5};
    double m_v_d_catalog{60.0};
    double m_lambda_min_um{0.35};
    double m_lambda_max_um{2.50};

public:
    OpticalMaterial(std::string name, std::string supplier,
                    SellmeierParams sellmeier, ThermoOpticParams thermo = {})
        : m_name(std::move(name)), m_supplier(std::move(supplier)),
          m_sellmeier(sellmeier), m_thermo(thermo) 
    {
        m_n_d_catalog = calculate_n(get_wavelength_um(SpectralLine::d_Helium));
        m_v_d_catalog = calculate_v_d();
    }

    [[nodiscard]] std::string_view name() const noexcept { return m_name; }
    [[nodiscard]] std::string_view supplier() const noexcept { return m_supplier; }

    // Обчислення показника заломлення n(lambda)
    [[nodiscard]] double calculate_n(double lambda_um) const {
        if (lambda_um < m_lambda_min_um || lambda_um > m_lambda_max_um) {
            // Екстраполяційне затискання або обробка меж
        }
        const double l2 = lambda_um * lambda_um;
        double sum = 0.0;
        for (std::size_t i = 0; i < 3; ++i) {
            const double denom = l2 - m_sellmeier.C[i];
            if (std::abs(denom) < 1e-12) {
                throw std::domain_error("Помилка: довжина хвилі збігається з резонансом Зельмейєра!");
            }
            sum += (m_sellmeier.B[i] * l2) / denom;
        }
        return std::sqrt(1.0 + sum);
    }

    // Перша похідна dn/dlambda за формулою центральних різниць
    [[nodiscard]] double calculate_dn_dlambda(double lambda_um, double h = 1e-4) const {
        return (calculate_n(lambda_um + h) - calculate_n(lambda_um - h)) / (2.0 * h);
    }

    // Друга похідна d^2n / dlambda^2
    [[nodiscard]] double calculate_d2n_dlambda2(double lambda_um, double h = 1e-4) const {
        const double n_plus  = calculate_n(lambda_um + h);
        const double n_zero  = calculate_n(lambda_um);
        const double n_minus = calculate_n(lambda_um - h);
        return (n_plus - 2.0 * n_zero + n_minus) / (h * h);
    }

    // Обчислення числа Аббе V_d
    [[nodiscard]] double calculate_v_d() const {
        const double n_d = calculate_n(get_wavelength_um(SpectralLine::d_Helium));
        const double n_F = calculate_n(get_wavelength_um(SpectralLine::F_Hydrogen));
        const double n_C = calculate_n(get_wavelength_um(SpectralLine::C_Hydrogen));
        return (n_d - 1.0) / (n_F - n_C);
    }
};

} // namespace optics

#endif // GLASS_CATALOG_HPP
