#include <iostream>
#include <string_view>
#include <cmath>
#include <numbers>
#include <expected>
#include <vector>
#include <iomanip>

namespace pcb::highspeed {

constexpr double SPEED_OF_LIGHT_MM_PS = 0.299792458; // мм / пс у вакуумі

enum class BusStandard {
    Usb2,
    Usb3,
    PcieGen3,
    PcieGen4,
    MipiCsi2,
    Ethernet1G
};

struct BusSpec {
    std::string_view name;
    double max_intra_skew_ps;
    double max_inter_skew_ps;
    double target_zdiff_ohm;
    double zdiff_tolerance_pct;
};

constexpr BusSpec get_bus_spec(BusStandard bus) noexcept {
    switch (bus) {
        case BusStandard::Usb2:        return { "USB 2.0 High Speed",  100.0, 500.0,  90.0, 10.0 };
        case BusStandard::Usb3:        return { "USB 3.0 SuperSpeed",   15.0, 100.0,  90.0, 10.0 };
        case BusStandard::PcieGen3:   return { "PCIe Gen3 (8 GT/s)",    5.0,  50.0, 100.0, 10.0 };
        case BusStandard::PcieGen4:   return { "PCIe Gen4 (16 GT/s)",   1.5,  25.0, 100.0, 10.0 };
        case BusStandard::MipiCsi2:   return { "MIPI CSI-2 (D-PHY)",    3.0,  10.0, 100.0, 10.0 };
        case BusStandard::Ethernet1G: return { "1000Base-T Ethernet",  50.0, 200.0, 100.0, 10.0 };
    }
    return { "Unknown", 0.0, 0.0, 100.0, 10.0 };
}

struct DiffPairMeasurement {
    double len_p_mm{ 0.0 };
    double len_n_mm{ 0.0 };
    double er_effective{ 3.2 };
    double measured_zdiff_ohm{ 100.0 };
};

struct ValidationReport {
    double delay_p_ps{ 0.0 };
    double delay_n_ps{ 0.0 };
    double intra_skew_ps{ 0.0 };
    bool is_skew_pass{ false };
    bool is_impedance_pass{ false };
    bool is_overall_pass{ false };
};

enum class ValidationError {
    InvalidLength,
    InvalidPermittivity,
    InvalidImpedance
};

class DiffPairValidator {
public:
    [[nodiscard]] static std::expected<ValidationReport, ValidationError>
    validate(BusStandard bus, const DiffPairMeasurement& meas) noexcept {
        if (meas.len_p_mm <= 0.0 || meas.len_n_mm <= 0.0) {
            return std::unexpected(ValidationError::InvalidLength);
        }
        if (meas.er_effective < 1.0) {
            return std::unexpected(ValidationError::InvalidPermittivity);
        }
        if (meas.measured_zdiff_ohm <= 0.0) {
            return std::unexpected(ValidationError::InvalidImpedance);
        }

        const auto spec = get_bus_spec(bus);
        const double v_prop = SPEED_OF_LIGHT_MM_PS / std::sqrt(meas.er_effective);

        ValidationReport report;
        report.delay_p_ps = meas.len_p_mm / v_prop;
        report.delay_n_ps = meas.len_n_mm / v_prop;
        report.intra_skew_ps = std::abs(report.delay_p_ps - report.delay_n_ps);

        report.is_skew_pass = (report.intra_skew_ps <= spec.max_intra_skew_ps);

        const double z_min = spec.target_zdiff_ohm * (1.0 - spec.zdiff_tolerance_pct / 100.0);
        const double z_max = spec.target_zdiff_ohm * (1.0 + spec.zdiff_tolerance_pct / 100.0);
        report.is_impedance_pass = (meas.measured_zdiff_ohm >= z_min && meas.measured_zdiff_ohm <= z_max);

        report.is_overall_pass = (report.is_skew_pass && report.is_impedance_pass);
        return report;
    }

    static void print_report(BusStandard bus, const DiffPairMeasurement& meas, const ValidationReport& report) {
        const auto spec = get_bus_spec(bus);
        std::cout << "====================================================\n"
                  << " Звіт валідації диференційної пари: " << spec.name << "\n"
                  << "====================================================\n"
                  << std::fixed << std::setprecision(3)
                  << " Довжина P / N      : " << meas.len_p_mm << " мм / " << meas.len_n_mm 
                  << " мм (ΔL = " << std::abs(meas.len_p_mm - meas.len_n_mm) << " мм)\n"
                  << std::setprecision(2)
                  << " Затримка P / N     : " << report.delay_p_ps << " пс / " << report.delay_n_ps << " пс\n"
                  << " Фазовий перекіс    : " << report.intra_skew_ps << " пс (Ліміт: <= " 
                  << spec.max_intra_skew_ps << " пс) -> " << (report.is_skew_pass ? "PASS" : "FAIL") << "\n"
                  << std::setprecision(1)
                  << " Імпеданс Z_diff    : " << meas.measured_zdiff_ohm << " Ом (Ціль: " 
                  << spec.target_zdiff_ohm << " ± " << spec.zdiff_tolerance_pct << "%) -> " 
                  << (report.is_impedance_pass ? "PASS" : "FAIL") << "\n"
                  << " Загальний висновок : " 
                  << (report.is_overall_pass ? "ГОДЕН ДЛЯ ВИРОБНИЦТВА" : "ПОТРІБНА РЕДАКЦІЯ ТРАСУВАННЯ") << "\n"
                  << "====================================================\n\n";
    }
};

} // namespace pcb::highspeed
