#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <random>
#include <iomanip>

constexpr std::size_t NUM_SUBCARRIERS = 64;
constexpr double PI = 3.14159265358979323846;

using Complex = std::complex<double>;

// Обчислення ДПФ для частотного представлення каналу
std::vector<Complex> compute_dft(const std::vector<Complex>& time_domain) {
    const std::size_t n = time_domain.size();
    std::vector<Complex> freq_domain(n, 0.0);
    for (std::size_t k = 0; k < n; ++k) {
        for (std::size_t m = 0; m < n; ++m) {
            double angle = -2.0 * PI * static_cast<double>(k * m) / static_cast<double>(n);
            freq_domain[k] += time_domain[m] * std::polar(1.0, angle);
        }
    }
    return freq_domain;
}

int main() {
    std::mt19937 rng(42);
    std::uniform_int_distribution<int> bit_dist(0, 1);

    // 1. Імпульсна характеристика багатопроменевого каналу h[n]
    std::vector<Complex> h_time(NUM_SUBCARRIERS, 0.0);
    h_time[0] = Complex(0.8, 0.0); // Пряма хвиля
    h_time[1] = Complex(0.6, 0.0); // Відбита хвиля (створює нуль у спектрі)

    const auto H_freq = compute_dft(h_time);

    // 2. Генерація 4-QAM символів
    std::vector<Complex> s_symbols(NUM_SUBCARRIERS);
    for (auto& sym : s_symbols) {
        double i_val = bit_dist(rng) ? 1.0 : -1.0;
        double q_val = bit_dist(rng) ? 1.0 : -1.0;
        sym = Complex(i_val, q_val) / std::sqrt(2.0);
    }

    const std::vector<double> snr_db_list = {10.0, 30.0};

    std::cout << "=== C++ Симуляція вирівнювання Zero-Forcing та MMSE ===\n\n";

    for (double snr_db : snr_db_list) {
        double snr_linear = std::pow(10.0, snr_db / 10.0);
        double sigma_w2 = 1.0 / snr_linear; // Відносна потужність шуму
        double noise_std = std::sqrt(sigma_w2 / 2.0);

        std::normal_distribution<double> noise_dist(0.0, noise_std);

        double mse_zf = 0.0;
        double mse_mmse = 0.0;

        for (std::size_t k = 0; k < NUM_SUBCARRIERS; ++k) {
            // Прийнятий сигнал у частотній області з шумом
            Complex noise(noise_dist(rng), noise_dist(rng));
            Complex y_k = H_freq[k] * s_symbols[k] + noise;

            // Zero-Forcing вирівнювач: W_zf = 1 / H
            Complex w_zf_k = Complex(1.0, 0.0) / H_freq[k];
            Complex s_zf_k = y_k * w_zf_k;

            // MMSE вирівнювач: W_mmse = H* / (|H|² + 1/SNR)
            double h_abs2 = std::norm(H_freq[k]);
            Complex w_mmse_k = std::conj(H_freq[k]) / (h_abs2 + sigma_w2);
            Complex s_mmse_k = y_k * w_mmse_k;

            // Накопичення квадрату помилки
            mse_zf += std::norm(s_zf_k - s_symbols[k]);
            mse_mmse += std::norm(s_mmse_k - s_symbols[k]);
        }

        mse_zf /= NUM_SUBCARRIERS;
        mse_mmse /= NUM_SUBCARRIERS;

        std::cout << std::fixed << std::setprecision(4);
        std::cout << "SNR = " << snr_db << " dB (sigma_w^2 = " << sigma_w2 << "):\n";
        std::cout << std::setprecision(6);
        std::cout << "  Zero-Forcing MSE : " << mse_zf << "\n";
        std::cout << "  MMSE MSE         : " << mse_mmse << "\n";
        std::cout << "  Виграш MMSE     : " << (mse_zf / mse_mmse) << "x менша помилка\n\n";
    }

    return 0;
}
