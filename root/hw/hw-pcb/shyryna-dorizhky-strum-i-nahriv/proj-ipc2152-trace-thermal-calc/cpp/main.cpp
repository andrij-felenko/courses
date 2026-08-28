#include <iostream>
#include <iomanip>
#include <cmath>
#include <numbers>
#include <expected>
#include <string_view>
#include <vector>

namespace pcb::thermal {

// Фізичні та технологічні константи
inline constexpr double RHO_CU_20C         = 1.7241e-8;  // Питомий опір міді при 20 °C (Ом·м)
inline constexpr double ALPHA_CU           = 0.00393;    // Температурний коефіцієнт опору (1/K)
inline constexpr double CU_DENSITY_KG_M3   = 8960.0;     // Густина міді (кг/м³)
inline constexpr double CU_SPEC_HEAT_J_KGK = 385.0;      // Питома теплоємність міді (Дж/(кг·К))
inline constexpr double OZ_TO_MM           = 0.0348;     // 1 oz фольга = 0.0348 мм
inline constexpr double MIL_TO_MM          = 0.0254;
inline constexpr double MM_TO_MIL          = 39.3700787;

// Константи апроксимації базової кривої IPC-2152
inline constexpr double K_BASE             = 0.0645;
inline constexpr double P_AREA             = 0.695;
inline constexpr double P_TEMP             = 0.435;

enum class CoolingMode {
    StillAirEnclosed,
    NaturalOpen,
    ForcedAir1ms,
    ForcedAir2_5ms,
    Vacuum
};

enum class CalcError {
    InvalidCurrent,
    InvalidTempRise,
    InvalidCopperThickness,
    NonConvergence
};

struct TraceParameters {
    double      current_a{5.0};
    double      temp_rise_c{20.0};
    double      ambient_temp_c{25.0};
    double      copper_oz{1.0};
    double      trace_length_mm{100.0};
    double      board_thickness_mm{1.6};
    double      distance_to_plane_mm{0.20};
    bool        is_internal{false};
    bool        has_ground_plane{true};
    CoolingMode cooling{CoolingMode::StillAirEnclosed};
};

struct TraceResult {
    double width_ipc2152_mm{0.0};
    double width_ipc2152_mils{0.0};
    double width_ipc2221_mm{0.0};
    double area_mm2{0.0};
    double current_density_a_mm2{0.0};
    double r_cold_mohm{0.0};
    double r_hot_mohm{0.0};
    double voltage_drop_mv{0.0};
    double power_loss_w{0.0};
    double joule_integral_i2t{0.0};
    int    min_vias_03mm{1};
    int    min_vias_05mm{1};
};

class Ipc2152Calculator {
public:
    [[nodiscard]] static constexpr double calculate_derating(const TraceParameters& p) noexcept {
        const double h = (p.board_thickness_mm > 0.4) ? p.board_thickness_mm : 1.6;
        const double m_thick = std::pow(h / 1.6, 0.125);

        double m_plane = 1.00;
        if (p.has_ground_plane) {
            const double d = (p.distance_to_plane_mm > 0.05) ? p.distance_to_plane_mm : 0.20;
            if (p.is_internal) {
                m_plane = 1.00 + 0.80 * std::exp(-d / 0.35);
            } else {
                m_plane = 1.00 + 0.50 * std::exp(-d / 0.35);
            }
        }

        const double oz = (p.copper_oz > 0.1) ? p.copper_oz : 1.0;
        double m_cu = 1.05 - 0.05 * (std::log(oz) / std::numbers::ln2);
        m_cu = std::clamp(m_cu, 0.90, 1.15);

        double m_env = 1.00;
        switch (p.cooling) {
            case CoolingMode::StillAirEnclosed: m_env = 1.00; break;
            case CoolingMode::NaturalOpen:       m_env = 1.15; break;
            case CoolingMode::ForcedAir1ms:     m_env = 1.45; break;
            case CoolingMode::ForcedAir2_5ms:   m_env = 1.85; break;
            case CoolingMode::Vacuum:           m_env = 0.70; break;
        }

        return m_thick * m_plane * m_cu * m_env;
    }

    [[nodiscard]] static std::expected<TraceResult, CalcError> calculate(const TraceParameters& p) noexcept {
        if (p.current_a <= 0.001) return std::unexpected(CalcError::InvalidCurrent);
        if (p.temp_rise_c < 0.5 || p.temp_rise_c > 150.0) return std::unexpected(CalcError::InvalidTempRise);
        if (p.copper_oz < 0.1 || p.copper_oz > 12.0) return std::unexpected(CalcError::InvalidCopperThickness);

        const double t_cu_mm = p.copper_oz * OZ_TO_MM;
        const double t_cu_mils = p.copper_oz * 1.378;
        const double total_derating = calculate_derating(p);

        // Пошук площі перерізу методом Ньютона
        double area = 0.10;
        bool converged = false;

        for (int iter = 0; iter < 50; ++iter) {
            const double i_model = K_BASE * std::pow(area, P_AREA) *
                                   std::pow(p.temp_rise_c, P_TEMP) * total_derating;
            const double f_val = i_model - p.current_a;

            if (std::abs(f_val) < 1e-6) {
                converged = true;
                break;
            }

            const double df_val = K_BASE * P_AREA * std::pow(area, P_AREA - 1.0) *
                                  std::pow(p.temp_rise_c, P_TEMP) * total_derating;
            if (std::abs(df_val) < 1e-12) break;

            area -= (f_val / df_val);
            if (area <= 1e-6) area = 1e-6;
        }

        if (!converged && area <= 1e-6) {
            return std::unexpected(CalcError::NonConvergence);
        }

        TraceResult res{};
        res.area_mm2 = area;
        res.width_ipc2152_mm = (area / t_cu_mm) + (0.35 * t_cu_mm);
        res.width_ipc2152_mils = res.width_ipc2152_mm * MM_TO_MIL;
        res.current_density_a_mm2 = p.current_a / area;

        // Порівняльний розрахунок за IPC-2221A
        const double k_2221 = p.is_internal ? 0.024 : 0.048;
        const double area_2221_mils2 = std::pow(p.current_a / (k_2221 * std::pow(p.temp_rise_c, 0.44)), 1.0 / 0.725);
        res.width_ipc2221_mm = (area_2221_mils2 / t_cu_mils) * MIL_TO_MM;

        // Електричні та теплові характеристики
        const double len_m = (p.trace_length_mm > 0.1 ? p.trace_length_mm : 100.0) * 1e-3;
        const double area_m2 = area * 1e-6;

        const double r_20c = RHO_CU_20C * (len_m / area_m2);
        const double t_final = p.ambient_temp_c + p.temp_rise_c;
        const double r_hot = r_20c * (1.0 + ALPHA_CU * (t_final - 20.0));

        res.r_cold_mohm = r_20c * 1e3;
        res.r_hot_mohm = r_hot * 1e3;
        res.voltage_drop_mv = p.current_a * res.r_hot_mohm;
        res.power_loss_w = p.current_a * p.current_a * (res.r_hot_mohm * 1e-3);
        res.joule_integral_i2t = p.current_a * p.current_a * 0.010;

        res.min_vias_03mm = static_cast<int>(std::ceil(p.current_a / 1.50));
        res.min_vias_05mm = static_cast<int>(std::ceil(p.current_a / 3.00));
        if (res.min_vias_03mm < 1) res.min_vias_03mm = 1;
        if (res.min_vias_05mm < 1) res.min_vias_05mm = 1;

        return res;
    }
};

} // namespace pcb::thermal

int main() {
    using namespace pcb::thermal;

    std::cout << "=================================================================\n";
    std::cout << "  ТЕСТУВАННЯ ТА ВЕРИФІКАЦІЯ КАЛЬКУЛЯТОРА IPC-2152 (C++20)\n";
    std::cout << "=================================================================\n\n";

    const std::vector<std::pair<std::string_view, TraceParameters>> test_cases = {
        {"Тест 1: 5 А, 1 oz, ΔT=20 °C, Зовнішній шар з GND екраном",
         TraceParameters{.current_a = 5.0, .temp_rise_c = 20.0, .ambient_temp_c = 25.0, .copper_oz = 1.0}},
        {"Тест 2: 15 А, 2 oz, ΔT=30 °C, Внутрішній силовий шар",
         TraceParameters{.current_a = 15.0, .temp_rise_c = 30.0, .ambient_temp_c = 25.0, .copper_oz = 2.0, .is_internal = true}},
        {"Тест 3: 30 А, 3 oz, ΔT=40 °C, Силова шина з обдувом 1.0 м/с",
         TraceParameters{.current_a = 30.0, .temp_rise_c = 40.0, .ambient_temp_c = 30.0, .copper_oz = 3.0, .cooling = CoolingMode::ForcedAir1ms}}
    };

    std::cout << std::fixed << std::setprecision(2);

    for (const auto& [name, params] : test_cases) {
        std::cout << "--- " << name << " ---\n";
        auto outcome = Ipc2152Calculator::calculate(params);
        if (outcome.has_value()) {
            const auto& res = outcome.value();
            std::cout << "  Ширина IPC-2152:           " << std::setw(6) << res.width_ipc2152_mm << " мм ("
                      << std::setw(6) << std::setprecision(1) << res.width_ipc2152_mils << " mils)\n" << std::setprecision(2);
            std::cout << "  Ширина IPC-2221 (стара):   " << std::setw(6) << res.width_ipc2221_mm << " мм\n";
            std::cout << "  Площа перерізу:            " << std::setw(6) << res.area_mm2 << " мм²\n";
            std::cout << "  Густина струму:            " << std::setw(6) << res.current_density_a_mm2 << " А/мм²\n";
            std::cout << "  Гарячий опір лінії:        " << std::setw(6) << res.r_hot_mohm << " мОм\n";
            std::cout << "  Падіння напруги:           " << std::setw(6) << res.voltage_drop_mv << " мВ\n";
            std::cout << "  Дисипація тепла:           " << std::setw(6) << res.power_loss_w << " Вт\n";
            std::cout << "  Матриця переходів (d=0.3): " << std::setw(2) << res.min_vias_03mm << " шт  (або "
                      << std::setw(2) << res.min_vias_05mm << " шт d=0.5 мм)\n\n";
        } else {
            std::cout << "  ПОМИЛКА РОЗРАХУНКУ!\n\n";
        }
    }

    return 0;
}
