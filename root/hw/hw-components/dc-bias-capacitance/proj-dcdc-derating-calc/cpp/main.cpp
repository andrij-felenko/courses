#include <iostream>
#include <iomanip>
#include <string_view>
#include <cmath>
#include <numbers>
#include <vector>
#include <span>

enum class DielectricClass {
    C0G,
    X7R,
    X5R,
    Y5V
};

enum class PackageSize {
    Pkg0402,
    Pkg0603,
    Pkg0805,
    Pkg1206,
    Pkg1210
};

struct MlccSpec {
    double nominal_cap_uf{10.0};
    double rated_voltage{16.0};
    DielectricClass dielectric{DielectricClass::X7R};
    PackageSize package_size{PackageSize::Pkg0805};
    double esr_mohm{3.0};
    int count{1};
};

struct BuckParams {
    double v_in{12.0};
    double v_out{5.0};
    double f_sw_khz{1000.0};
    double l_ind_uh{2.2};
    double i_step_a{1.5};
    double t_resp_us{8.0};
};

struct OutputMetrics {
    double eff_cap_per_unit_uf;
    double eff_total_cap_uf;
    double retention_pct;
    double inductor_ripple_a;
    double v_ripple_nom_mv;
    double v_ripple_actual_mv;
    double pole_nom_khz;
    double pole_actual_khz;
    double v_sag_actual_mv;
    bool is_stable;
};

class MlccBiasAnalyzer {
public:
    [[nodiscard]] static constexpr std::string_view to_string(DielectricClass d) noexcept {
        switch (d) {
            case DielectricClass::C0G: return "C0G/NP0 (Клас I)";
            case DielectricClass::X7R: return "X7R (Клас II)";
            case DielectricClass::X5R: return "X5R (Клас II)";
            case DielectricClass::Y5V: return "Y5V (Клас III)";
        }
        return "Невідомий";
    }

    [[nodiscard]] static constexpr std::string_view to_string(PackageSize p) noexcept {
        switch (p) {
            case PackageSize::Pkg0402: return "0402 (1.0x0.5 мм)";
            case PackageSize::Pkg0603: return "0603 (1.6x0.8 мм)";
            case PackageSize::Pkg0805: return "0805 (2.0x1.25 мм)";
            case PackageSize::Pkg1206: return "1206 (3.2x1.6 мм)";
            case PackageSize::Pkg1210: return "1210 (3.2x2.5 мм)";
        }
        return "Невідомий";
    }

    [[nodiscard]] static double calculate_retention(const MlccSpec& spec, double v_dc) noexcept {
        if (spec.dielectric == DielectricClass::C0G || v_dc <= 0.0) {
            return 1.0;
        }

        double v_half_ratio = 0.50;
        switch (spec.package_size) {
            case PackageSize::Pkg0402: v_half_ratio = 0.30; break;
            case PackageSize::Pkg0603: v_half_ratio = 0.45; break;
            case PackageSize::Pkg0805: v_half_ratio = 0.60; break;
            case PackageSize::Pkg1206: v_half_ratio = 0.85; break;
            case PackageSize::Pkg1210: v_half_ratio = 1.10; break;
        }

        double gamma = 1.40;
        switch (spec.dielectric) {
            case DielectricClass::X7R:
                gamma = 1.40;
                break;
            case DielectricClass::X5R:
                gamma = 1.65;
                v_half_ratio *= 0.85;
                break;
            case DielectricClass::Y5V:
                gamma = 2.40;
                v_half_ratio *= 0.40;
                break;
            default:
                break;
        }

        const double v_half = spec.rated_voltage * v_half_ratio;
        const double normalized = v_dc / v_half;
        const double retention = 1.0 / (1.0 + std::pow(normalized, gamma));

        return std::max(retention, 0.02);
    }

    [[nodiscard]] static OutputMetrics evaluate(const MlccSpec& cap, const BuckParams& pwr) noexcept {
        const double retention = calculate_retention(cap, pwr.v_out);
        const double eff_unit = cap.nominal_cap_uf * retention;
        const double eff_total = eff_unit * cap.count;
        const double nom_total = cap.nominal_cap_uf * cap.count;

        const double f_sw_hz = pwr.f_sw_khz * 1e3;
        const double l_h = pwr.l_ind_uh * 1e-6;
        const double i_rip = (pwr.v_in - pwr.v_out) * pwr.v_out / (f_sw_hz * l_h * pwr.v_in);

        const double c_nom_f = nom_total * 1e-6;
        const double c_eff_f = eff_total * 1e-6;
        const double esr_total_ohm = (cap.esr_mohm * 1e-3) / cap.count;

        const double v_rip_esr = i_rip * esr_total_ohm;
        const double v_rip_nom = (i_rip / (8.0 * f_sw_hz * c_nom_f) + v_rip_esr) * 1e3;
        const double v_rip_act = (i_rip / (8.0 * f_sw_hz * c_eff_f) + v_rip_esr) * 1e3;

        const double pole_nom = (1.0 / (2.0 * std::numbers::pi * std::sqrt(l_h * c_nom_f))) * 1e-3;
        const double pole_act = (1.0 / (2.0 * std::numbers::pi * std::sqrt(l_h * c_eff_f))) * 1e-3;

        const double t_resp_s = pwr.t_resp_us * 1e-6;
        const double v_sag_act = (pwr.i_step_a * t_resp_s / c_eff_f) * 1e3;

        const bool stable = (pole_act / pole_nom) <= 1.60;

        return {
            .eff_cap_per_unit_uf = eff_unit,
            .eff_total_cap_uf = eff_total,
            .retention_pct = retention * 100.0,
            .inductor_ripple_a = i_rip,
            .v_ripple_nom_mv = v_rip_nom,
            .v_ripple_actual_mv = v_rip_act,
            .pole_nom_khz = pole_nom,
            .pole_actual_khz = pole_act,
            .v_sag_actual_mv = v_sag_act,
            .is_stable = stable
        };
    }

    static void print_report(const MlccSpec& cap, const BuckParams& pwr, const OutputMetrics& m) {
        std::cout << "==================================================================\n"
                  << "  АНАЛІЗ DC-BIAS ДЕРАТИНГУ ДЛЯ ВИХОДУ DCDC (C++20)\n"
                  << "==================================================================\n"
                  << "Конфігурація: " << pwr.v_in << " В -> " << pwr.v_out << " В, "
                  << pwr.f_sw_khz << " кГц, L = " << pwr.l_ind_uh << " мкГн\n"
                  << "Конденсатори: " << cap.count << " x " << cap.nominal_cap_uf << " мкФ "
                  << to_string(cap.dielectric) << " " << to_string(cap.package_size)
                  << " (" << cap.rated_voltage << " В номінал)\n\n"
                  << std::fixed << std::setprecision(2)
                  << "Результати моделювання:\n"
                  << "  Залишок ємності:              " << m.retention_pct << " %\n"
                  << "  Сумарна ефективна ємність:    " << m.eff_total_cap_uf << " мкФ (номінал "
                  << (cap.nominal_cap_uf * cap.count) << " мкФ)\n"
                  << "  Пульсації напруги (робочі):   " << m.v_ripple_actual_mv << " мВ (номінальні "
                  << m.v_ripple_nom_mv << " мВ)\n"
                  << "  Просідання при стрибку 1.5 А: " << m.v_sag_actual_mv << " мВ\n"
                  << "  Зсув резонансного полюса:     " << m.pole_nom_khz << " кГц -> "
                  << m.pole_actual_khz << " кГц (x" << (m.pole_actual_khz / m.pole_nom_khz) << ")\n"
                  << "  Статус стабільності контуру:  "
                  << (m.is_stable ? "[ СТІЙКИЙ ]" : "[ КРИТИЧНИЙ ЗСУВ ПОЛЮСА / РИЗИК ДЗВОНУ ]")
                  << "\n==================================================================\n\n";
    }
};

int main() {
    const BuckParams buck_cfg{
        .v_in = 12.0,
        .v_out = 5.0,
        .f_sw_khz = 1000.0,
        .l_ind_uh = 2.2,
        .i_step_a = 1.5,
        .t_resp_us = 8.0
    };

    const std::vector<MlccSpec> test_suite = {
        { .nominal_cap_uf = 22.0, .rated_voltage = 10.0, .dielectric = DielectricClass::X5R, .package_size = PackageSize::Pkg0603, .esr_mohm = 4.0, .count = 2 },
        { .nominal_cap_uf = 22.0, .rated_voltage = 25.0, .dielectric = DielectricClass::X7R, .package_size = PackageSize::Pkg1206, .esr_mohm = 3.0, .count = 2 },
        { .nominal_cap_uf = 10.0, .rated_voltage = 50.0, .dielectric = DielectricClass::C0G, .package_size = PackageSize::Pkg1210, .esr_mohm = 2.0, .count = 4 }
    };

    for (const auto& cap : test_suite) {
        const auto metrics = MlccBiasAnalyzer::evaluate(cap, buck_cfg);
        MlccBiasAnalyzer::print_report(cap, buck_cfg, metrics);
    }

    return 0;
}
