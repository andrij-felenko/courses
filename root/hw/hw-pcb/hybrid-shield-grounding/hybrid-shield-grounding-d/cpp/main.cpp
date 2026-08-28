/*
 * Модуль розрахунку імпедансу гібридного заземлення екрана (C++20).
 * Застосовує типізовані комплексні структури, std::span та constexpr математику.
 */

#include <iostream>
#include <iomanip>
#include <complex>
#include <vector>
#include <span>
#include <numbers>
#include <cmath>

struct HybridGroundParams {
    double r_bleed_ohm{1.0e6};       // Опір витоку, 1 МОм
    double c_rf_farad{10.0e-9};       // ВЧ ємність, 10 нФ
    double esl_henry{1.5e-9};         // Паразитна індуктивність ESL, 1.5 нГн
    double esr_ohm{0.02};             // Активний опір втрат ESR, 20 мОм
    double v_gnd_rms_volts{10.0};     // Різниця потенціалів земель, 10 В
};

struct GroundPointResult {
    double freq_hz{0.0};
    std::complex<double> z_hybrid_ohm{0.0, 0.0};
    double i_loop_rms_amps{0.0};
    double attenuation_db{0.0};

    [[nodiscard]] double magnitude() const noexcept {
        return std::abs(z_hybrid_ohm);
    }
};

class HybridShieldModel {
public:
    explicit constexpr HybridShieldModel(HybridGroundParams params) noexcept
        : params_(params) {}

    [[nodiscard]] GroundPointResult evaluate(double freq_hz) const noexcept {
        GroundPointResult result;
        result.freq_hz = freq_hz;

        if (freq_hz <= 0.0) {
            result.z_hybrid_ohm = {params_.r_bleed_ohm, 0.0};
            result.i_loop_rms_amps = params_.v_gnd_rms_volts / params_.r_bleed_ohm;
            result.attenuation_db = 0.0;
            return result;
        }

        const double omega = 2.0 * std::numbers::pi * freq_hz;
        const double xc = 1.0 / (omega * params_.c_rf_farad);
        const double xl = omega * params_.esl_henry;

        // Повний комплексний імпеданс конденсаторної гілки
        const std::complex<double> z_cap{params_.esr_ohm, xl - xc};
        const std::complex<double> z_res{params_.r_bleed_ohm, 0.0};

        // Паралельний імпеданс: Z = (Z_cap * Z_res) / (Z_cap + Z_res)
        result.z_hybrid_ohm = (z_cap * z_res) / (z_cap + z_res);

        const double mag = std::abs(result.z_hybrid_ohm);
        result.i_loop_rms_amps = (mag > 1e-12) ? (params_.v_gnd_rms_volts / mag) : 0.0;
        result.attenuation_db = -20.0 * std::log10(mag / (mag + 50.0));

        return result;
    }

    [[nodiscard]] std::vector<GroundPointResult> sweep(std::span<const double> freqs) const {
        std::vector<GroundPointResult> results;
        results.reserve(freqs.size());
        for (double f : freqs) {
            results.push_back(evaluate(f));
        }
        return results;
    }

private:
    HybridGroundParams params_;
};

int main() {
    const HybridGroundParams cfg{
        .r_bleed_ohm = 1.0e6,
        .c_rf_farad = 10.0e-9,
        .esl_henry = 1.5e-9,
        .esr_ohm = 0.02,
        .v_gnd_rms_volts = 10.0
    };

    const HybridShieldModel model{cfg};
    const std::vector<double> freqs{ 50.0, 1.0e3, 100.0e3, 1.0e6, 10.0e6, 50.0e6, 100.0e6 };

    std::cout << std::left << std::setw(14) << "Частота [Гц]"
              << std::setw(18) << "|Z_hybrid| [Ом]"
              << std::setw(16) << "I_loop [мкА]"
              << "Послаблення [дБ]\n";
    std::cout << std::string(64, '-') << "\n";

    for (const auto& r : model.sweep(freqs)) {
        std::cout << std::left << std::setw(14) << std::fixed << std::setprecision(1) << r.freq_hz
                  << std::setw(18) << std::setprecision(4) << r.magnitude()
                  << std::setw(16) << std::setprecision(3) << (r.i_loop_rms_amps * 1.0e6)
                  << std::setprecision(2) << r.attenuation_db << "\n";
    }

    return 0;
}
