#include <iostream>
#include <numbers>
#include <cmath>
#include <expected>
#include <string_view>
#include <format>

struct CrystalSpec {
    double freq_hz{16'000'000.0};
    double load_cap_pf{12.0};
    double esr_ohm{30.0};
    double shunt_cap_pf{3.0};
    double drive_level_max_uw{100.0};
};

struct DriverSpec {
    double gm_uA_per_V{3000.0};
    double vdd_volts{3.3};
    double pcb_stray_pf{3.5};
};

struct CalculationReport {
    double c_ext_pf{0.0};
    double gm_crit_uA_per_V{0.0};
    double gain_margin{0.0};
    double rd_opt_ohm{0.0};
    bool is_reliable{false};
};

enum class CalcError {
    InvalidParameters,
    StrayExceedsLoadCap
};

[[nodiscard]] constexpr std::expected<CalculationReport, CalcError>
analyze_oscillator(const CrystalSpec& xtal, const DriverSpec& driver) noexcept
{
    if (xtal.freq_hz <= 0.0 || xtal.load_cap_pf <= 0.0 || xtal.esr_ohm <= 0.0) {
        return std::unexpected(CalcError::InvalidParameters);
    }
    if (driver.pcb_stray_pf >= xtal.load_cap_pf) {
        return std::unexpected(CalcError::StrayExceedsLoadCap);
    }

    CalculationReport rep{};
    rep.c_ext_pf = 2.0 * (xtal.load_cap_pf - driver.pcb_stray_pf);

    const double omega = 2.0 * std::numbers::pi * xtal.freq_hz;
    const double c_tot_f = (xtal.shunt_cap_pf + xtal.load_cap_pf) * 1e-12;
    const double gm_crit_si = 4.0 * xtal.esr_ohm * std::pow(omega * c_tot_f, 2);

    rep.gm_crit_uA_per_V = gm_crit_si * 1e6;
    rep.gain_margin = driver.gm_uA_per_V / rep.gm_crit_uA_per_V;
    rep.is_reliable = (rep.gain_margin >= 5.0);

    const double c2_f = rep.c_ext_pf * 1e-12;
    rep.rd_opt_ohm = 1.0 / (omega * c2_f);

    return rep;
}

int main()
{
    constexpr CrystalSpec xtal_16mhz{
        .freq_hz = 16.0e6,
        .load_cap_pf = 12.0,
        .esr_ohm = 30.0,
        .shunt_cap_pf = 3.0,
        .drive_level_max_uw = 100.0
    };

    constexpr DriverSpec mcu_spec{
        .gm_uA_per_V = 3000.0,
        .vdd_volts = 3.3,
        .pcb_stray_pf = 3.5
    };

    const auto result = analyze_oscillator(xtal_16mhz, mcu_spec);

    if (result.has_value()) {
        const auto& r = result.value();
        std::cout << std::format("Параметри контуру HSE 16 МГц:\n");
        std::cout << std::format("  Зовнішні C1, C2:  {:.2f} пФ (стандарт 18 пФ C0G)\n", r.c_ext_pf);
        std::cout << std::format("  Критична gm:      {:.2f} мкА/В\n", r.gm_crit_uA_per_V);
        std::cout << std::format("  Запас підсилення: {:.2f} (статус: {})\n",
                                 r.gain_margin, r.is_reliable ? "НАДІЙНИЙ" : "ЗРИВ");
        std::cout << std::format("  Демпфуючий Rd:    {:.1f} Ом\n", r.rd_opt_ohm);
    } else {
        std::cerr << "Помилка розрахунку контуру кварцу!\n";
    }

    return 0;
}
