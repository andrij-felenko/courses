#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>

struct MagnonWave {
    double amplitude{1.0};
    double phase_rad{0.0};
    double frequency_hz{10.0e9};
};

struct MagnonicGateResult {
    double input_phase_a{0.0};
    double input_phase_b{0.0};
    double output_intensity{0.0};
    bool logic_bit_xor{false};
    bool logic_bit_and{false};
};

struct DattaDasParams {
    double alpha_r_ev_m{0.0};          // Параметр Рашби (еВ·м)
    double channel_length_m{200.0e-9}; // Довжина каналу (м)
    double m_eff_kg{0.023 * 9.1093837015e-31}; // Ефективна маса електрона
};

class SpintronicSimulator {
public:
    static constexpr double HBAR = 1.054571817e-34;
    static constexpr double EV_TO_JOULE = 1.602176634e-19;

    [[nodiscard]] static MagnonicGateResult simulate_magnonic_gate(
        const MagnonWave& w1, 
        const MagnonWave& w2, 
        double threshold) noexcept 
    {
        MagnonicGateResult result{};
        result.input_phase_a = w1.phase_rad;
        result.input_phase_b = w2.phase_rad;

        const double delta_phi = w1.phase_rad - w2.phase_rad;
        const double i1 = w1.amplitude * w1.amplitude;
        const double i2 = w2.amplitude * w2.amplitude;

        result.output_intensity = i1 + i2 + 2.0 * std::sqrt(i1 * i2) * std::cos(delta_phi);
        result.logic_bit_xor = (std::abs(delta_phi) > 0.5 * std::numbers::pi);
        result.logic_bit_and = (result.output_intensity >= threshold);

        return result;
    }

    [[nodiscard]] static double simulate_datta_das_current(const DattaDasParams& p) noexcept {
        const double alpha_j = p.alpha_r_ev_m * EV_TO_JOULE;
        const double delta_theta = (2.0 * p.m_eff_kg * alpha_j * p.channel_length_m) / (HBAR * HBAR);
        const double cos_val = std::cos(delta_theta / 2.0);
        return cos_val * cos_val;
    }
};

int main() {
    std::cout << "=== Спінтронічний Симулятор (C++20) ===\n";
    std::cout << std::fixed << std::setprecision(3);

    const std::vector<double> phases{0.0, std::numbers::pi};
    constexpr double threshold = 3.0;

    std::cout << "Phase A | Phase B | Intensity | XOR | AND\n";
    std::cout << "------------------------------------------\n";

    for (double p1 : phases) {
        for (double p2 : phases) {
            MagnonWave w1{.amplitude = 1.0, .phase_rad = p1};
            MagnonWave w2{.amplitude = 1.0, .phase_rad = p2};

            const auto res = SpintronicSimulator::simulate_magnonic_gate(w1, w2, threshold);
            std::cout << " " << res.input_phase_a << "  |  " << res.input_phase_b 
                      << "  |   " << res.output_intensity 
                      << "   |  " << res.logic_bit_xor 
                      << "  |  " << res.logic_bit_and << "\n";
        }
    }

    std::cout << "\n=== Залежність провідності Spin-FET від полем Рашби ===\n";
    DattaDasParams params{.channel_length_m = 200.0e-9};

    for (int i = 0; i <= 5; ++i) {
        params.alpha_r_ev_m = i * 0.4e-11;
        const double current = SpintronicSimulator::simulate_datta_das_current(params);
        const double theta = (2.0 * params.m_eff_kg * params.alpha_r_ev_m * 
                              SpintronicSimulator::EV_TO_JOULE * params.channel_length_m) / 
                             (SpintronicSimulator::HBAR * SpintronicSimulator::HBAR);

        std::cout << "Alpha_R: " << std::scientific << std::setprecision(2) << params.alpha_r_ev_m 
                  << " eV*m | Theta: " << std::fixed << std::setprecision(3) << theta 
                  << " rad | Current: " << current << "\n";
    }

    return 0;
}
