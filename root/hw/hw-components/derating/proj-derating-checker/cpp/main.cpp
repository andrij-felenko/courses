#include <iostream>
#include <string_view>
#include <vector>
#include <iomanip>
#include <algorithm>

enum class Standard {
    MilHdbk338B,
    Ipc9592BClass2,
    Commercial
};

enum class ComponentType {
    ResistorFilm,
    CapCeramicX7R,
    CapTantalumMnO2,
    CapAluElectrolytic,
    SemiconductorMosfet,
    SemiconductorDiode,
    InductorPower
};

struct ComponentRating {
    std::string_view designator;
    ComponentType type;
    double v_rated;        // В
    double i_rated;        // А
    double p_rated;        // Вт
    double t_knee;         // °C
    double t_max;          // °C
    double rth_ja;         // °C/Вт
};

struct OperatingCondition {
    double v_actual_peak;  // В
    double i_actual_rms;   // А
    double p_actual_diss;  // Вт
    double ta_ambient;     // °C
};

struct StandardLimits {
    double max_s_v;
    double max_s_i;
    double max_s_p;
    double max_tj;
};

struct DeratingReport {
    bool passed{true};
    double s_v{0.0};
    double s_i{0.0};
    double s_p{0.0};
    double tj_actual{0.0};
    double p_allowed_derated{0.0};
    std::string_view violation_reason{"OK"};
};

class DeratingAuditor {
public:
    static constexpr StandardLimits get_limits(ComponentType type, Standard std) noexcept {
        if (std == Standard::MilHdbk338B) {
            switch (type) {
                case ComponentType::ResistorFilm:        return { 0.70, 0.70, 0.50, 105.0 };
                case ComponentType::CapTantalumMnO2:    return { 0.50, 0.50, 0.50, 105.0 };
                case ComponentType::CapCeramicX7R:      return { 0.60, 0.70, 0.60, 105.0 };
                case ComponentType::CapAluElectrolytic: return { 0.70, 0.70, 0.50, 85.0 };
                case ComponentType::SemiconductorMosfet: return { 0.75, 0.70, 0.50, 110.0 };
                case ComponentType::SemiconductorDiode:  return { 0.70, 0.50, 0.50, 105.0 };
                case ComponentType::InductorPower:       return { 0.80, 0.70, 0.60, 105.0 };
            }
        } else if (std == Standard::Ipc9592BClass2) {
            switch (type) {
                case ComponentType::ResistorFilm:        return { 0.80, 0.80, 0.65, 115.0 };
                case ComponentType::CapTantalumMnO2:    return { 0.50, 0.70, 0.65, 115.0 };
                case ComponentType::CapCeramicX7R:      return { 0.70, 0.75, 0.70, 115.0 };
                case ComponentType::CapAluElectrolytic: return { 0.80, 0.75, 0.70, 105.0 };
                case ComponentType::SemiconductorMosfet: return { 0.80, 0.75, 0.65, 120.0 };
                case ComponentType::SemiconductorDiode:  return { 0.80, 0.70, 0.70, 115.0 };
                case ComponentType::InductorPower:       return { 0.85, 0.80, 0.70, 115.0 };
            }
        }
        return { 0.90, 0.85, 0.80, 130.0 }; // Commercial
    }

    static DeratingReport evaluate(const ComponentRating& rat, const OperatingCondition& op, Standard std) noexcept {
        DeratingReport report{};
        const auto limits = get_limits(rat.type, std);

        report.s_v = (rat.v_rated > 0.0) ? (op.v_actual_peak / rat.v_rated) : 0.0;
        report.s_i = (rat.i_rated > 0.0) ? (op.i_actual_rms / rat.i_rated) : 0.0;

        double p_nominal_at_temp = rat.p_rated;
        if (op.ta_ambient > rat.t_knee) {
            if (op.ta_ambient >= rat.t_max) {
                p_nominal_at_temp = 0.0;
            } else {
                p_nominal_at_temp = rat.p_rated * ((rat.t_max - op.ta_ambient) / (rat.t_max - rat.t_knee));
            }
        }

        report.p_allowed_derated = p_nominal_at_temp * limits.max_s_p;
        report.s_p = (p_nominal_at_temp > 0.0) ? (op.p_actual_diss / p_nominal_at_temp) : 999.0;
        report.tj_actual = op.ta_ambient + (op.p_actual_diss * rat.rth_ja);

        if (report.s_v > limits.max_s_v) {
            report.passed = false;
            report.violation_reason = "Voltage limit exceeded";
        } else if (report.s_i > limits.max_s_i) {
            report.passed = false;
            report.violation_reason = "Current limit exceeded";
        } else if (op.p_actual_diss > report.p_allowed_derated) {
            report.passed = false;
            report.violation_reason = "Thermal derated power exceeded";
        } else if (report.tj_actual > limits.max_tj) {
            report.passed = false;
            report.violation_reason = "Junction temperature Tj exceeded";
        }

        return report;
    }
};

int main() {
    const ComponentRating mosfet{
        "Q1_PowerMOS",
        ComponentType::SemiconductorMosfet,
        60.0, 40.0, 45.0, 25.0, 150.0, 2.8
    };

    const OperatingCondition op{
        48.0, 18.0, 12.0, 65.0
    };

    std::cout << "=== АУДИТ ДЕРАТИНГУ (C++) ДЛЯ " << mosfet.designator << " ===\n";

    const auto report_mil = DeratingAuditor::evaluate(mosfet, op, Standard::MilHdbk338B);
    std::cout << "[MIL-HDBK-338B] Статус: " << (report_mil.passed ? "ВІДПОВІДАЄ" : "ДЕФЕКТ")
              << " | S_v: " << std::fixed << std::setprecision(2) << report_mil.s_v
              << " | Tj: " << std::setprecision(1) << report_mil.tj_actual << " C"
              << " | Причина: " << report_mil.violation_reason << "\n";

    const auto report_ipc = DeratingAuditor::evaluate(mosfet, op, Standard::Ipc9592BClass2);
    std::cout << "[IPC-9592B-Cl2]  Статус: " << (report_ipc.passed ? "ВІДПОВІДАЄ" : "ДЕФЕКТ")
              << " | S_v: " << std::fixed << std::setprecision(2) << report_ipc.s_v
              << " | Tj: " << std::setprecision(1) << report_ipc.tj_actual << " C"
              << " | Причина: " << report_ipc.violation_reason << "\n";

    return 0;
}
