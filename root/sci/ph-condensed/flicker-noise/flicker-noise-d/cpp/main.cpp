#include <vector>
#include <cmath>
#include <random>
#include <complex>
#include <span>

// Проста реалізація дискретного перетворення Фур'є для генерації 1/f шуму
std::vector<double> generate_flicker_noise(size_t num_samples) {
    std::vector<std::complex<double>> spectrum(num_samples / 2 + 1);
    std::mt19937 gen(1337);
    std::uniform_real_distribution<double> dist(0.0, 2.0 * M_PI);

    spectrum[0] = 0.0; // Нульове DC зміщення
    for (size_t k = 1; k < spectrum.size(); ++k) {
        double freq = static_cast<double>(k);
        double amp = 1.0 / std::sqrt(freq);
        double phase = dist(gen);
        spectrum[k] = std::polar(amp, phase);
    }

    // Зворотне ДПФ для розрахунку відліків у часовій області
    std::vector<double> noise(num_samples, 0.0);
    double N = static_cast<double>(num_samples);
    for (size_t n = 0; n < num_samples; ++n) {
        double sum = 0.0;
        for (size_t k = 1; k < spectrum.size(); ++k) {
            double angle = 2.0 * M_PI * k * n / N;
            sum += spectrum[k].real() * std::cos(angle) - spectrum[k].imag() * std::sin(angle);
        }
        noise[n] = sum;
    }
    return noise;
}
