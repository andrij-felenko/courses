#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <numeric>
#include <iomanip>
#include <string>

// Структура результату моделювання
struct CaptureResult {
    double ratio_db;
    double suppression_db;
    std::string captured_signal;
};

// Функція симуляції приймача ЧМ з ідеальним обмежувачем
CaptureResult simulate_fm_capture(double carrier_ratio_db, double fs = 480000.0, double duration = 0.1) {
    const size_t num_samples = static_cast<size_t>(fs * duration);
    const double dt = 1.0 / fs;
    
    const double f_mod1 = 400.0;
    const double dev1 = 75000.0;
    
    const double f_mod2 = 1000.0;
    const double dev2 = 75000.0;
    const double f_offset = 5000.0;
    
    const double a2 = std::pow(10.0, -carrier_ratio_db / 20.0);
    
    std::vector<std::complex<double>> s_lim(num_samples);
    
    // 1. Генерація та нормування вхідного сумарного сигналу
    for (size_t k = 0; k < num_samples; ++k) {
        double t = k * dt;
        
        double phi1 = (dev1 / f_mod1) * std::sin(2.0 * std::numbers::pi * f_mod1 * t);
        std::complex<double> s1 = std::exp(std::complex<double>(0.0, phi1));
        
        double phi2 = 2.0 * std::numbers::pi * f_offset * t + (dev2 / f_mod2) * std::sin(2.0 * std::numbers::pi * f_mod2 * t);
        std::complex<double> s2 = a2 * std::exp(std::complex<double>(0.0, phi2));
        
        std::complex<double> s_sum = s1 + s2;
        s_lim[k] = s_sum / std::abs(s_sum); // Нормування обмежувачем
    }
    
    // 2. Демодуляція миттєвої частоти квадратурним дискримінатором
    std::vector<double> freq_inst(num_samples - 1);
    for (size_t k = 1; k < num_samples; ++k) {
        std::complex<double> d = s_lim[k] * std::conj(s_lim[k - 1]);
        freq_inst[k - 1] = std::arg(d) * (fs / (2.0 * std::numbers::pi));
    }
    
    // 3. Точне вимірювання потужностей тонів методом Герцеля (Goertzel Algorithm)
    auto goertzel_magnitude = [&](double target_freq) {
        double omega = 2.0 * std::numbers::pi * target_freq / fs;
        double coeff = 2.0 * std::cos(omega);
        double q1 = 0.0, q2 = 0.0;
        for (double sample : freq_inst) {
            double q0 = coeff * q1 - q2 + sample;
            q2 = q1;
            q1 = q0;
        }
        return std::sqrt(q1 * q1 + q2 * q2 - coeff * q1 * q2);
    };
    
    double mag1 = goertzel_magnitude(f_mod1);
    double mag2 = goertzel_magnitude(f_mod2);
    
    double supp_db = 20.0 * std::log10(mag1 / (mag2 + 1e-12));
    std::string captured = (carrier_ratio_db > 0.0) ? "Сигнал 1 (400 Гц)" : "Сигнал 2 (1000 Гц)";
    
    return {carrier_ratio_db, supp_db, captured};
}

int main() {
    std::cout << "=== Результати моделювання ефекту захоплення ЧМ (C++20) ===\n";
    std::vector<double> test_ratios = {-10.0, -6.0, -2.0, -0.5, 0.5, 2.0, 6.0, 12.0};
    
    for (double r : test_ratios) {
        auto res = simulate_fm_capture(r);
        std::cout << "Співвідношення A1/A2 = " << std::setw(5) << std::fixed << std::setprecision(1) << res.ratio_db
                  << " дБ | Придушення: " << std::setw(6) << std::setprecision(1) << res.suppression_db
                  << " дБ | Захоплено: " << res.captured_signal << "\n";
    }
    return 0;
}
