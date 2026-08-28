/*
 * Hybrid Shield Grounding Impedance & Shielding Effectiveness Calculator
 * Standard: ISO/IEC 14882:2020 (C++20)
 *
 * Compilation:
 *   g++ -std=c++20 -O3 -Wall -Wextra proj-hybrid-shield-calc.cpp -o hybrid_calc_cpp
 *   clang++ -std=c++20 -O3 -Wall -Wextra proj-hybrid-shield-calc.cpp -o hybrid_calc_cpp
 */

#include <iostream>
#include <iomanip>
#include <vector>
#include <complex>
#include <span>
#include <numbers>
#include <cmath>
#include <string>
#include <string_view>
#include <algorithm>

namespace emc {

inline constexpr double Mu0 = 4.0 * std::numbers::pi * 1.0e-7;
inline constexpr double CopperSigma = 5.8e7;

struct CableSpec {
    double length_m{50.0};
    double r_dc_per_m{0.0145};
    double braid_diameter_m{0.0060};
    double wire_diameter_m{0.00016};
    double optical_coverage{0.90};
    double l_ext_per_m{0.85e-6};
};

struct HybridTerminationSpec {
    double r_bleed_ohm{1.0e6};
    double c_rf_farad{10.0e-9};
    double esl_henry{1.5e-9};
    double esr_ohm{0.02};
    double c_gdt_farad{1.0e-12};
    double v_gnd_rms_volts{10.0};
    double v_cap_rating_volts{2000.0};
};

struct FrequencyPointResult {
    double freq_hz{0.0};
    std::complex<double> z_transfer_per_m{0.0, 0.0};
    std::complex<double> z_hybrid_node{0.0, 0.0};
    std::complex<double> z_loop_total{0.0, 0.0};
    double i_loop_rms_amps{0.0};
    double v_noise_cm_volts{0.0};
    double shielding_effectiveness_db{0.0};
    double v_cap_peak_volts{0.0};
    double p_res_watts{0.0};

    [[nodiscard]] bool is_voltage_safe(double rating_v) const noexcept {
        return v_cap_peak_volts <= rating_v * 0.7;
    }
};

class HybridShieldSolver {
public:
    HybridShieldSolver(CableSpec cable, HybridTerminationSpec term) noexcept
        : cable_(cable), term_(term) {}

    [[nodiscard]] static double calculate_skin_depth(double freq_hz) noexcept {
        if (freq_hz <= 1.0) return 0.066;
        return std::sqrt(1.0 / (std::numbers::pi * freq_hz * Mu0 * CopperSigma));
    }

    [[nodiscard]] std::complex<double> calculate_transfer_impedance(double freq_hz) const noexcept {
        if (freq_hz <= 0.0) {
            return {cable_.r_dc_per_m, 0.0};
        }

        const double delta = calculate_skin_depth(freq_hz);
        const double d = 2.0 * cable_.wire_diameter_m;
        const std::complex<double> gamma{(1.0) / delta, (1.0) / delta};
        const std::complex<double> gamma_d = gamma * d;

        std::complex<double> z_diff;
        if (std::abs(gamma_d) < 1e-4) {
            z_diff = {cable_.r_dc_per_m, 0.0};
        } else {
            z_diff = cable_.r_dc_per_m * (gamma_d / std::sinh(gamma_d));
        }

        const double k_cov = std::clamp(cable_.optical_coverage, 0.50, 0.99);
        const double m_h = (Mu0 / (6.0 * std::numbers::pi)) * std::pow(1.0 - k_cov, 1.5) *
                           (d / (cable_.braid_diameter_m * 0.5));
        const std::complex<double> z_hole{0.0, 2.0 * std::numbers::pi * freq_hz * m_h};

        return z_diff + z_hole;
    }

    [[nodiscard]] std::complex<double> calculate_hybrid_node_impedance(double freq_hz) const noexcept {
        if (freq_hz <= 0.0) {
            return {term_.r_bleed_ohm, 0.0};
        }

        const double omega = 2.0 * std::numbers::pi * freq_hz;
        const double xc = 1.0 / (omega * term_.c_rf_farad);
        const double xl = omega * term_.esl_henry;

        const std::complex<double> z_cap{term_.esr_ohm, xl - xc};
        const std::complex<double> z_res{term_.r_bleed_ohm, 0.0};
        const std::complex<double> z_gdt{0.0, -1.0 / (omega * term_.c_gdt_farad)};

        const std::complex<double> y_total = (1.0 / z_cap) + (1.0 / z_res) + (1.0 / z_gdt);
        return 1.0 / y_total;
    }

    [[nodiscard]] FrequencyPointResult solve_point(double freq_hz) const noexcept {
        FrequencyPointResult r;
        r.freq_hz = freq_hz;

        r.z_transfer_per_m = calculate_transfer_impedance(freq_hz);
        r.z_hybrid_node = calculate_hybrid_node_impedance(freq_hz);

        const double omega = 2.0 * std::numbers::pi * freq_hz;
        const double delta = calculate_skin_depth(freq_hz);
        const double r_skin_factor = (delta > 0.0) ? (cable_.wire_diameter_m / (2.0 * delta)) : 1.0;
        const double r_ac_per_m = cable_.r_dc_per_m * std::max(1.0, r_skin_factor);
        const std::complex<double> z_shield_ext = (std::complex<double>{r_ac_per_m, omega * cable_.l_ext_per_m}) * cable_.length_m;

        const std::complex<double> z_contact_a{0.005, omega * 0.5e-9};
        r.z_loop_total = z_contact_a + z_shield_ext + r.z_hybrid_node;

        const double z_loop_mag = std::abs(r.z_loop_total);
        r.i_loop_rms_amps = (z_loop_mag > 1e-12) ? (term_.v_gnd_rms_volts / z_loop_mag) : 0.0;

        const std::complex<double> v_noise_vec = std::complex<double>{r.i_loop_rms_amps, 0.0} * r.z_transfer_per_m * cable_.length_m;
        r.v_noise_cm_volts = std::abs(v_noise_vec);

        if (r.v_noise_cm_volts > 1e-12 && term_.v_gnd_rms_volts > 1e-12) {
            r.shielding_effectiveness_db = 20.0 * std::log10(term_.v_gnd_rms_volts / r.v_noise_cm_volts);
        } else {
            r.shielding_effectiveness_db = 120.0;
        }

        const double v_hybrid_rms = r.i_loop_rms_amps * std::abs(r.z_hybrid_node);
        r.v_cap_peak_volts = v_hybrid_rms * std::numbers::sqrt2;
        r.p_res_watts = (v_hybrid_rms * v_hybrid_rms) / term_.r_bleed_ohm;

        return r;
    }

    [[nodiscard]] std::vector<FrequencyPointResult> solve_sweep(std::span<const double> freqs) const {
        std::vector<FrequencyPointResult> results;
        results.reserve(freqs.size());
        for (double f : freqs) {
            results.push_back(solve_point(f));
        }
        return results;
    }

private:
    CableSpec cable_;
    HybridTerminationSpec term_;
};

} // namespace emc

int main(int argc, char** argv) {
    emc::CableSpec cable{
        .length_m = 50.0,
        .r_dc_per_m = 0.0145,
        .braid_diameter_m = 0.0060,
        .wire_diameter_m = 0.00016,
        .optical_coverage = 0.90,
        .l_ext_per_m = 0.85e-6
    };

    emc::HybridTerminationSpec term{
        .r_bleed_ohm = 1.0e6,
        .c_rf_farad = 10.0e-9,
        .esl_henry = 1.5e-9,
        .esr_ohm = 0.02,
        .c_gdt_farad = 1.0e-12,
        .v_gnd_rms_volts = 10.0,
        .v_cap_rating_volts = 2000.0
    };

    bool csv_mode = false;
    for (int i = 1; i < argc; ++i) {
        std::string_view arg{argv[i]};
        if (arg == "--csv") csv_mode = true;
    }

    const std::vector<double> freqs{
        10.0, 50.0, 100.0, 1.0e3, 10.0e3, 100.0e3,
        500.0e3, 1.0e6, 5.0e6, 10.0e6, 25.0e6, 50.0e6,
        100.0e6, 250.0e6, 500.0e6, 1000.0e6
    };

    const emc::HybridShieldSolver solver{cable, term};
    const auto results = solver.solve_sweep(freqs);

    if (csv_mode) {
        std::cout << "Frequency_Hz,Z_hybrid_Ohm,Z_loop_Ohm,I_loop_uA,V_noise_mV,SE_dB,V_cap_V\n";
        for (const auto& r : results) {
            std::cout << r.freq_hz << ","
                      << std::abs(r.z_hybrid_node) << ","
                      << std::abs(r.z_loop_total) << ","
                      << (r.i_loop_rms_amps * 1.0e6) << ","
                      << (r.v_noise_cm_volts * 1.0e3) << ","
                      << r.shielding_effectiveness_db << ","
                      << r.v_cap_peak_volts << "\n";
        }
    } else {
        std::cout << "\n====================================================================================================\n";
        std::cout << "        ЧАСТОТНИЙ АНАЛІЗ ГІБРИДНОГО ЗАЗЕМЛЕННЯ ЕКРАНА КАБЕЛЮ (C++20 ISO/IEC 14882)          \n";
        std::cout << "====================================================================================================\n";
        std::cout << " Частота [Гц] | |Z_hyb| [Ом] | |Z_loop| [Ом] | I_loop [мкА] | V_noise [мВ] | SE [дБ] | V_cap [В] | Стан \n";
        std::cout << "--------------+--------------+---------------+--------------+--------------+---------+-----------+------\n";

        for (const auto& r : results) {
            std::cout << " " << std::setw(12) << std::fixed << std::setprecision(1) << r.freq_hz
                      << " | " << std::setw(12) << std::setprecision(3) << std::abs(r.z_hybrid_node)
                      << " | " << std::setw(13) << std::setprecision(3) << std::abs(r.z_loop_total)
                      << " | " << std::setw(12) << std::setprecision(2) << (r.i_loop_rms_amps * 1.0e6)
                      << " | " << std::setw(12) << std::setprecision(4) << (r.v_noise_cm_volts * 1.0e3)
                      << " | " << std::setw(7) << std::setprecision(1) << r.shielding_effectiveness_db
                      << " | " << std::setw(9) << std::setprecision(3) << r.v_cap_peak_volts
                      << " | " << (r.is_voltage_safe(term.v_cap_rating_volts) ? "НОРМА" : "УВАГА!")
                      << "\n";
        }
        std::cout << "====================================================================================================\n\n";
    }

    return 0;
}
