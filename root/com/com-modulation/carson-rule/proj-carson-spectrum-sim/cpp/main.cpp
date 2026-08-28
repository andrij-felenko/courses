#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <numeric>

class FmSpectrumAnalyzer {
public:
    struct AnalysisResult {
        double beta;
        double carson_bandwidth_hz;
        double carson_power_ratio;
        std::size_t harmonic_count_carson;
        std::size_t harmonic_count_98pct;
        std::size_t harmonic_count_99pct;
    };

    static AnalysisResult analyze(double carrier_freq, double mod_freq, double dev_freq, std::size_t fft_size = 8192) {
        const double beta = dev_freq / mod_freq;
        const double carson_bw = 2.0 * (dev_freq + mod_freq);
        const auto n_carson = static_cast<std::size_t>(std::floor(beta + 1.0));
        const double fs = carrier_freq * 8.0;

        std::vector<std::complex<double>> signal(fft_size);

        // Синтез сигналу з вікном Ханна
        for (std::size_t i = 0; i < fft_size; ++i) {
            const double t = static_cast<double>(i) / fs;
            const double phase = 2.0 * std::numbers::pi * carrier_freq * t + beta * std::sin(2.0 * std::numbers::pi * mod_freq * t);
            const double window = 0.5 * (1.0 - std::cos(2.0 * std::numbers::pi * static_cast<double>(i) / static_cast<double>(fft_size - 1)));
            signal[i] = std::polar(window, phase);
        }

        compute_fft(signal);

        std::vector<double> power(fft_size / 2);
        double total_power = 0.0;

        for (std::size_t i = 0; i < fft_size / 2; ++i) {
            power[i] = std::norm(signal[i]);
            total_power += power[i];
        }

        const double bin_res = fs / static_cast<double>(fft_size);
        const auto carrier_bin = static_cast<std::size_t>(std::round(carrier_freq / bin_res));
        const auto mod_bin_step = static_cast<std::size_t>(std::round(mod_freq / bin_res));

        double carson_power = power[carrier_bin];
        for (std::size_t n = 1; n <= n_carson; ++n) {
            if (carrier_bin >= n * mod_bin_step) {
                carson_power += power[carrier_bin - n * mod_bin_step];
            }
            if (carrier_bin + n * mod_bin_step < fft_size / 2) {
                carson_power += power[carrier_bin + n * mod_bin_step];
            }
        }

        std::size_t n_98 = 0;
        std::size_t n_99 = 0;
        double accum_power = power[carrier_bin];

        for (std::size_t n = 1; n < fft_size / 4; ++n) {
            if (carrier_bin >= n * mod_bin_step) {
                accum_power += power[carrier_bin - n * mod_bin_step];
            }
            if (carrier_bin + n * mod_bin_step < fft_size / 2) {
                accum_power += power[carrier_bin + n * mod_bin_step];
            }

            const double ratio = accum_power / total_power;
            if (ratio >= 0.98 && n_98 == 0) n_98 = n;
            if (ratio >= 0.99 && n_99 == 0) {
                n_99 = n;
                break;
            }
        }

        return {
            .beta = beta,
            .carson_bandwidth_hz = carson_bw,
            .carson_power_ratio = carson_power / total_power,
            .harmonic_count_carson = n_carson,
            .harmonic_count_98pct = n_98,
            .harmonic_count_99pct = n_99
        };
    }

private:
    static void compute_fft(std::vector<std::complex<double>>& x) {
        const std::size_t n = x.size();
        if (n <= 1) return;

        std::vector<std::complex<double>> even(n / 2), odd(n / 2);
        for (std::size_t i = 0; i < n / 2; ++i) {
            even[i] = x[2 * i];
            odd[i]  = x[2 * i + 1];
        }

        compute_fft(even);
        compute_fft(odd);

        for (std::size_t k = 0; k < n / 2; ++k) {
            const auto t = std::polar(1.0, -2.0 * std::numbers::pi * static_cast<double>(k) / static_cast<double>(n)) * odd[k];
            x[k]           = even[k] + t;
            x[k + n / 2]   = even[k] - t;
        }
    }
};

int main() {
    const double mod_freq = 15000.0;
    const std::vector<double> deviations = { 7500.0, 15000.0, 36072.0, 75000.0, 150000.0 };

    std::cout << "=== Аналіз спектра ЧМ за правилом Карсона (C++20) ===\n\n";
    std::cout << std::left << std::setw(8)  << "β"
              << " | " << std::setw(8)  << "Δf (кГц)"
              << " | " << std::setw(12) << "B_Carson"
              << " | " << std::setw(12) << "Потужність"
              << " | " << std::setw(10) << "N_Carson"
              << " | " << std::setw(10) << "N_98%\n";
    std::cout << std::string(72, '-') << "\n";

    for (double dev : deviations) {
        const auto r = FmSpectrumAnalyzer::analyze(1000000.0, mod_freq, dev);
        std::cout << std::left << std::setw(8)  << std::fixed << std::setprecision(2) << r.beta
                  << " | " << std::setw(8)  << std::setprecision(1) << dev / 1000.0
                  << " | " << std::setw(10) << std::setprecision(1) << r.carson_bandwidth_hz / 1000.0 << " кГц"
                  << " | " << std::setw(10) << std::setprecision(2) << r.carson_power_ratio * 100.0 << "%"
                  << " | " << std::setw(10) << r.harmonic_count_carson
                  << " | " << std::setw(10) << r.harmonic_count_98pct << "\n";
    }

    return 0;
}
