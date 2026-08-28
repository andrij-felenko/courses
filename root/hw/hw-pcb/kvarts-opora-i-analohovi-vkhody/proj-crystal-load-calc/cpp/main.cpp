#include <iostream>
#include <numbers>
#include <cmath>
#include <expected>
#include <string_view>
#include <format>
#include <array>

namespace pcb_precision {

// ── 1. Типізовані структури модуля кварцового генератора ──────────────
struct CrystalParameters {
    double freq_hz{16'000'000.0};
    double load_cap_pf{12.0};
    double esr_ohm{35.0};
    double shunt_cap_pf{3.0};
    double drive_level_max_uw{100.0};
};

struct DriverParameters {
    double gm_uA_per_V{2500.0};
    double vdd_volts{3.3};
    double pcb_stray_pf{3.5};
};

struct CrystalEvaluation {
    double c_ext_pf{0.0};
    double gm_crit_uA_per_V{0.0};
    double gain_margin{0.0};
    double drive_level_uw{0.0};
    double rd_opt_ohm{0.0};
    bool is_startup_reliable{false};
    bool is_power_safe{false};
};

enum class DomainError {
    InvalidInput,
    StrayExceedsNominal,
    NegativeImpedance
};

[[nodiscard]] constexpr std::expected<CrystalEvaluation, DomainError>
analyze_crystal(const CrystalParameters& xtal, const DriverParameters& drv) noexcept
{
    if (xtal.freq_hz <= 0.0 || xtal.load_cap_pf <= 0.0 || xtal.esr_ohm <= 0.0) {
        return std::unexpected(DomainError::InvalidInput);
    }
    if (drv.pcb_stray_pf >= xtal.load_cap_pf) {
        return std::unexpected(DomainError::StrayExceedsNominal);
    }

    CrystalEvaluation res{};
    res.c_ext_pf = 2.0 * (xtal.load_cap_pf - drv.pcb_stray_pf);

    const double omega = 2.0 * std::numbers::pi * xtal.freq_hz;
    const double c_tot_f = (xtal.shunt_cap_pf + xtal.load_cap_pf) * 1e-12;
    const double gm_crit_si = 4.0 * xtal.esr_ohm * std::pow(omega * c_tot_f, 2);

    res.gm_crit_uA_per_V = gm_crit_si * 1e6;
    res.gain_margin = drv.gm_uA_per_V / res.gm_crit_uA_per_V;
    res.is_startup_reliable = (res.gain_margin >= 5.0);

    const double c2_f = res.c_ext_pf * 1e-12;
    res.rd_opt_ohm = 1.0 / (omega * c2_f);

    const double i_drive = std::numbers::pi * xtal.freq_hz * c_tot_f * drv.vdd_volts;
    res.drive_level_uw = (2.0 * xtal.esr_ohm * i_drive * i_drive) * 1e6;
    res.is_power_safe = (res.drive_level_uw <= xtal.drive_level_max_uw);

    return res;
}

// ── 2. Типізовані структури модуля АЦП ─────────────────────────────────
struct AdcParameters {
    unsigned int resolution_bits{16};
    double c_sample_pf{15.0};
    double r_on_ohm{400.0};
    double t_acq_configured_ns{150.0};
    double r_ext_ohm{47.0};
    double c_ext_pf{1000.0};
};

struct AdcEvaluation {
    double cap_ratio{0.0};
    double tau_ns{0.0};
    double t_acq_min_ns{0.0};
    double settling_error_lsb{0.0};
    double cutoff_freq_khz{0.0};
    bool is_cap_ratio_ok{false};
    bool is_settling_complete{false};
};

[[nodiscard]] constexpr std::expected<AdcEvaluation, DomainError>
analyze_adc(const AdcParameters& adc) noexcept
{
    if (adc.resolution_bits == 0 || adc.c_sample_pf <= 0.0 || adc.r_on_ohm < 0.0) {
        return std::unexpected(DomainError::InvalidInput);
    }

    AdcEvaluation res{};
    res.cap_ratio = adc.c_ext_pf / adc.c_sample_pf;
    res.is_cap_ratio_ok = (res.cap_ratio >= 20.0);

    const double r_tot = adc.r_ext_ohm + adc.r_on_ohm;
    const double c_sample_f = adc.c_sample_pf * 1e-12;
    const double tau_s = r_tot * c_sample_f;

    res.tau_ns = tau_s * 1e9;
    const double k_settle = (adc.resolution_bits + 1) * std::numbers::ln2;
    res.t_acq_min_ns = k_settle * res.tau_ns;

    const double t_acq_s = adc.t_acq_configured_ns * 1e-9;
    const double exp_val = std::exp(-t_acq_s / tau_s);
    const double total_quantums = std::pow(2.0, static_cast<double>(adc.resolution_bits));

    res.settling_error_lsb = total_quantums * exp_val;
    res.is_settling_complete = (res.settling_error_lsb < 0.5);

    const double c_ext_f = adc.c_ext_pf * 1e-12;
    if (adc.r_ext_ohm > 0.0 && c_ext_f > 0.0) {
        const double fc_hz = 1.0 / (2.0 * std::numbers::pi * adc.r_ext_ohm * c_ext_f);
        res.cutoff_freq_khz = fc_hz / 1e3;
    }

    return res;
}

// ── 3. Типізовані структури модуля феритового фільтра ─────────────────
struct FerriteParameters {
    double bead_inductance_uh{2.2};
    double bead_rdc_ohm{0.08};
    double cap_uf{10.0};
    double cap_esr_ohm{0.005};
};

struct FerriteEvaluation {
    double f_res_khz{0.0};
    double q_factor{0.0};
    double peak_gain_db{0.0};
    double rdamp_needed_ohm{0.0};
    bool is_damped{false};
};

[[nodiscard]] constexpr std::expected<FerriteEvaluation, DomainError>
analyze_ferrite(const FerriteParameters& fb) noexcept
{
    if (fb.bead_inductance_uh <= 0.0 || fb.cap_uf <= 0.0) {
        return std::unexpected(DomainError::InvalidInput);
    }

    FerriteEvaluation res{};
    const double l_h = fb.bead_inductance_uh * 1e-6;
    const double c_f = fb.cap_uf * 1e-6;
    const double r_tot = fb.rdc_ohm + fb.cap_esr_ohm;

    const double f_res_hz = 1.0 / (2.0 * std::numbers::pi * std::sqrt(l_h * c_f));
    res.f_res_khz = f_res_hz / 1e3;

    res.q_factor = (1.0 / r_tot) * std::sqrt(l_h / c_f);
    res.is_damped = (res.q_factor <= 0.70710678);
    res.peak_gain_db = (res.q_factor > 1.0) ? (20.0 * std::log10(res.q_factor)) : 0.0;

    const double r_crit = std::sqrt(2.0 * l_h / c_f);
    res.rdamp_needed_ohm = (r_crit > fb.bead_rdc_ohm) ? (r_crit - fb.bead_rdc_ohm) : 0.0;

    return res;
}

} // namespace pcb_precision

int main()
{
    using namespace pcb_precision;

    std::cout << "=======================================================================\n";
    std::cout << "     C++20 ПРЕЦИЗІЙНИЙ МОДУЛЬ ДІАГНОСТИКИ ТОПОЛОГІЇ ДРУКОВАНОЇ ПЛАТИ   \n";
    std::cout << "=======================================================================\n\n";

    // 1. Аналіз кварцу
    constexpr CrystalParameters xtal_16mhz{
        .freq_hz = 16.0e6,
        .load_cap_pf = 12.0,
        .esr_ohm = 35.0,
        .shunt_cap_pf = 3.0,
        .drive_level_max_uw = 100.0
    };
    constexpr DriverParameters mcu_drv{
        .gm_uA_per_V = 2500.0,
        .vdd_volts = 3.3,
        .pcb_stray_pf = 3.5
    };

    if (const auto res = analyze_crystal(xtal_16mhz, mcu_drv); res.has_value()) {
        const auto& r = res.value();
        std::cout << std::format("▼ [Кварцовий генератор HSE 16.0 МГц]\n");
        std::cout << std::format("  - Конденсатори C1, C2:     {:.2f} пФ (стандарт E24: 18 пФ C0G)\n", r.c_ext_pf);
        std::cout << std::format("  - Критична крутизна:       {:.2f} мкА/В\n", r.gm_crit_uA_per_V);
        std::cout << std::format("  - Коефіцієнт Gain Margin:  {:.2f} [{}]\n",
                                 r.gain_margin, r.is_startup_reliable ? "СТІЙКИЙ" : "ЗРИВ");
        std::cout << std::format("  - Демпфуючий резистор Rd:  {:.1f} Ом\n", r.rd_opt_ohm);
        std::cout << std::format("  - Потужність збудження:    {:.2f} мкВт [{}]\n\n",
                                 r.drive_level_uw, r.is_power_safe ? "НОРМА" : "ПЕРЕВАНТАЖЕННЯ");
    }

    // 2. Аналіз АЦП
    constexpr AdcParameters adc_16bit{
        .resolution_bits = 16,
        .c_sample_pf = 15.0,
        .r_on_ohm = 400.0,
        .t_acq_configured_ns = 150.0,
        .r_ext_ohm = 47.0,
        .c_ext_pf = 1000.0
    };

    if (const auto res = analyze_adc(adc_16bit); res.has_value()) {
        const auto& r = res.value();
        std::cout << std::format("▼ [16-розрядний тракт S&H АЦП]\n");
        std::cout << std::format("  - Співвідношення ємностей: {:.1f} [{}]\n",
                                 r.cap_ratio, r.is_cap_ratio_ok ? "НОРМА" : "МАЛО");
        std::cout << std::format("  - Постійна часу tau:       {:.2f} нс\n", r.tau_ns);
        std::cout << std::format("  - Мін. час вибірки t_acq:  {:.2f} нс (налаштовано: {:.1f} нс)\n",
                                 r.t_acq_min_ns, adc_16bit.t_acq_configured_ns);
        std::cout << std::format("  - Похибка встановлення:    {:.6f} LSB [{}]\n",
                                 r.settling_error_lsb, r.is_settling_complete ? "ТОЧНО" : "ПОХИБКА");
        std::cout << std::format("  - Смуга RC-фільтра:        {:.2f} кГц\n\n", r.cutoff_freq_khz);
    }

    // 3. Аналіз феритового фільтра
    constexpr FerriteParameters fb_spec{
        .bead_inductance_uh = 2.2,
        .bead_rdc_ohm = 0.08,
        .cap_uf = 10.0,
        .cap_esr_ohm = 0.005
    };

    if (const auto res = analyze_ferrite(fb_spec); res.has_value()) {
        const auto& r = res.value();
        std::cout << std::format("▼ [Фільтр аналогового живлення VDDA]\n");
        std::cout << std::format("  - Резонансна частота:      {:.2f} кГц\n", r.f_res_khz);
        std::cout << std::format("  - Добротність контуру Q:   {:.2f} [{}]\n",
                                 r.q_factor, r.is_damped ? "ЗАКРИТИЧНО" : "СПЛЕСК");
        std::cout << std::format("  - Пік підсилення завад:    +{:.2f} дБ\n", r.peak_gain_db);
        std::cout << std::format("  - Необхідний демпфер:      {:.3f} Ом\n", r.rdamp_needed_ohm);
    }

    std::cout << "=======================================================================\n";
    return 0;
}
