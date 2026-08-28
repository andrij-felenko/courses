#include <iostream>
#include <vector>
#include <cmath>
#include <complex>
#include <numbers>
#include <iomanip>

struct HornSegment {
    double position_m;
    double diameter_m;
    double area_m2;
};

struct ImpedanceSample {
    double frequency_hz;
    double active_resistance;
    double reactive_reactance;
    std::complex<double> complex_impedance;
};

class ExponentialHornSimulator {
private:
    double throat_diameter_m_;
    double mouth_diameter_m_;
    double cutoff_freq_hz_;
    double speed_of_sound_m_s_;
    double air_density_kg_m3_;
    
    double S0_;
    double SL_;
    double flare_rate_m_;
    double horn_length_m_;

public:
    ExponentialHornSimulator(double throat_d, double mouth_d, double cutoff_f, 
                             double c = 343.0, double rho = 1.204)
        : throat_diameter_m_(throat_d), mouth_diameter_m_(mouth_d),
          cutoff_freq_hz_(cutoff_f), speed_of_sound_m_s_(c), air_density_kg_m3_(rho) {
        
        S0_ = std::numbers::pi * throat_diameter_m_ * throat_diameter_m_ / 4.0;
        SL_ = std::numbers::pi * mouth_diameter_m_ * mouth_diameter_m_ / 4.0;
        flare_rate_m_ = (4.0 * std::numbers::pi * cutoff_freq_hz_) / speed_of_sound_m_s_;
        horn_length_m_ = std::log(SL_ / S0_) / flare_rate_m_;
    }
    
    [[nodiscard]] double get_length() const noexcept { return horn_length_m_; }
    [[nodiscard]] double get_flare_rate() const noexcept { return flare_rate_m_; }

    [[nodiscard]] std::vector<HornSegment> generate_profile(std::size_t steps = 100) const {
        std::vector<HornSegment> profile;
        profile.reserve(steps + 1);
        
        for (std::size_t i = 0; i <= steps; ++i) {
            double x = (horn_length_m_ * static_cast<double>(i)) / static_cast<double>(steps);
            double Sx = S0_ * std::exp(flare_rate_m_ * x);
            double dx = 2.0 * std::sqrt(Sx / std::numbers::pi);
            profile.push_back({x, dx, Sx});
        }
        return profile;
    }
    
    [[nodiscard]] std::vector<ImpedanceSample> compute_infinite_impedance_spectrum(
            double max_freq_factor = 3.0, std::size_t num_samples = 100) const {
        
        std::vector<ImpedanceSample> spectrum;
        spectrum.reserve(num_samples);
        
        const double Z0_throat = (air_density_kg_m3_ * speed_of_sound_m_s_) / S0_;
        
        for (std::size_t i = 1; i <= num_samples; ++i) {
            double f = (max_freq_factor * cutoff_freq_hz_ * static_cast<double>(i)) / static_cast<double>(num_samples);
            double r_norm = 0.0;
            double x_norm = 0.0;
            
            if (f >= cutoff_freq_hz_) {
                r_norm = std::sqrt(1.0 - (cutoff_freq_hz_ / f) * (cutoff_freq_hz_ / f));
                x_norm = cutoff_freq_hz_ / f;
            } else {
                r_norm = 0.0;
                x_norm = f / cutoff_freq_hz_;
            }
            
            std::complex<double> z_comp(r_norm * Z0_throat, x_norm * Z0_throat);
            spectrum.push_back({f, r_norm, x_norm, z_comp});
        }
        return spectrum;
    }
};

int main() {
    ExponentialHornSimulator simulator(0.0254, 0.30, 400.0);
    
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "C++ Експоненційний симулятор рупора:\n";
    std::cout << "Довжина: " << simulator.get_length() << " м\n";
    std::cout << "Показник розширення m: " << simulator.get_flare_rate() << " м^-1\n";
    
    auto spectrum = simulator.compute_infinite_impedance_spectrum(3.0, 100);
    std::cout << "Нормований активний опір на 800 Гц: " << spectrum[66].active_resistance << "\n";
    
    return 0;
}
