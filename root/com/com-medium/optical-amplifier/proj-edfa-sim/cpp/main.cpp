#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <span>
#include <expected>
#include <format>

namespace optics {

constexpr double planck_constant = 6.62607015e-34;
constexpr double speed_of_light = 2.99792458e8;
constexpr double bw_optical_01nm = 12.5e9;

struct WdmChannel {
    double wavelength_nm{1550.0};
    double power_dbm{-10.0};
};

struct EdfaConfig {
    double small_signal_gain_db{20.0};
    double sat_power_dbm{15.0};
    double noise_figure_db{4.5};
};

struct CascadeResult {
    double total_output_power_dbm;
    double accumulated_ase_dbm;
    double osnr_db;
};

enum class SimError {
    InvalidChannelCount,
    NegativeSpanLoss,
    InvalidGain
};

[[nodiscard]] constexpr double dbm_to_watts(double dbm) noexcept {
    return 1e-3 * std::pow(10.0, dbm / 10.0);
}

[[nodiscard]] constexpr double watts_to_dbm(double watts) noexcept {
    if (watts <= 0.0) return -100.0;
    return 10.0 * std::log10(watts / 1e-3);
}

class EdfaSimulator {
public:
    [[nodiscard]] static double solve_gain(double g0_linear, double psat_watts, double pin_total_watts) noexcept {
        if (pin_total_watts <= 0.0) return g0_linear;
        
        double g = g0_linear;
        constexpr double tol = 1e-7;
        constexpr int max_iter = 100;
        
        for (int i = 0; i < max_iter; ++i) {
            const double exp_factor = std::exp(-(g - 1.0) * (pin_total_watts / psat_watts));
            const double f_val = g - g0_linear * exp_factor;
            
            if (std::abs(f_val) < tol) break;
            
            const double df_dg = 1.0 + g0_linear * exp_factor * (pin_total_watts / psat_watts);
            g -= f_val / df_dg;
            if (g < 1.0) g = 1.0;
        }
        return g;
    }

    [[nodiscard]] static std::expected<CascadeResult, SimError> simulate_cascade(
        std::span<const WdmChannel> channels,
        double span_loss_db,
        const EdfaConfig& edfa,
        int num_spans) noexcept 
    {
        if (channels.empty()) return std::unexpected(SimError::InvalidChannelCount);
        if (span_loss_db < 0.0) return std::unexpected(SimError::NegativeSpanLoss);
        
        double pin_total_watts = 0.0;
        for (const auto& ch : channels) {
            pin_total_watts += dbm_to_watts(ch.power_dbm);
        }
        
        const double g0_linear = std::pow(10.0, edfa.small_signal_gain_db / 10.0);
        const double psat_watts = dbm_to_watts(edfa.sat_power_dbm);
        const double nf_linear = std::pow(10.0, edfa.noise_figure_db / 10.0);
        
        const double nsp = std::max(1.0, nf_linear / 2.0);
        
        double current_signal_watts = pin_total_watts;
        double accumulated_ase_watts = 0.0;
        
        const double span_attenuation_linear = std::pow(10.0, -span_loss_db / 10.0);
        constexpr double freq_hz = speed_of_light / 1550e-9;
        
        for (int span = 0; span < num_spans; ++span) {
            current_signal_watts *= span_attenuation_linear;
            accumulated_ase_watts *= span_attenuation_linear;
            
            const double total_in_watts = current_signal_watts + accumulated_ase_watts;
            const double g_actual = solve_gain(g0_linear, psat_watts, total_in_watts);
            
            current_signal_watts *= g_actual;
            accumulated_ase_watts *= g_actual;
            
            const double single_stage_ase = 2.0 * nsp * (g_actual - 1.0) * planck_constant * freq_hz * bw_optical_01nm;
            accumulated_ase_watts += single_stage_ase;
        }
        
        const double ch1_pout_watts = dbm_to_watts(channels[0].power_dbm) * (current_signal_watts / pin_total_watts);
        const double osnr_db = 10.0 * std::log10(ch1_pout_watts / (accumulated_ase_watts / static_cast<double>(channels.size())));
        
        return CascadeResult{
            .total_output_power_dbm = watts_to_dbm(current_signal_watts),
            .accumulated_ase_dbm = watts_to_dbm(accumulated_ase_watts),
            .osnr_db = osnr_db
        };
    }
};

} // namespace optics

int main() {
    std::vector<optics::WdmChannel> wdm_system(8);
    for (std::size_t i = 0; i < wdm_system.size(); ++i) {
        wdm_system[i].wavelength_nm = 1550.0 + static_cast<double>(i) * 0.8;
        wdm_system[i].power_dbm = -10.0;
    }
    
    constexpr optics::EdfaConfig edfa{
        .small_signal_gain_db = 20.0,
        .sat_power_dbm = 15.0,
        .noise_figure_db = 4.5
    };
    
    constexpr int spans = 10;
    constexpr double span_loss_db = 18.0;
    
    auto result = optics::EdfaSimulator::simulate_cascade(wdm_system, span_loss_db, edfa, spans);
    
    if (result) {
        std::cout << std::format("=== Результати симуляції лінки EDFA (C++) ({}, {} дБ) ===\n", spans, span_loss_db);
        std::cout << std::format("Загальна вихідна потужність сигналу: {:.2f} дБм\n", result->total_output_power_dbm);
        std::cout << std::format("Накопичена потужність шуму ASE (0.1 нм): {:.2f} дБм\n", result->accumulated_ase_dbm);
        std::cout << std::format("Оптичне відношення сигнал/шум (OSNR): {:.2f} дБ\n", result->osnr_db);
    } else {
        std::cerr << "Помилка під час обчислення каскаду підсилювачів.\n";
    }
    
    return 0;
}
