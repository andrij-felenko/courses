#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <numbers>
#include <string>

// Структура фізичної конфігурації двохщілинного досліду
struct ExperimentConfig {
    double wavelength = 0.167e-9;        // Довжина хвилі де Бройля електрона (0.167 нм при V = 54 В)
    double slit_distance = 1.0e-6;        // Відстань між щілинами d (1 мкм)
    double slit_width = 0.2e-6;           // Ширина однієї щілини b (0.2 мкм)
    double screen_dist = 0.5;             // Відстань від щілин до екрана D (0.5 м)
    double screen_half_width = 0.002;     // Напівширина детекторного екрана (2 мм)
    size_t num_bins = 100;                // Кількість комірок гістограми
};

// Обчислення теоретичної ймовірності влучання в координату y
double calculate_probability(double y, const ExperimentConfig& cfg) {
    const double pi = std::numbers::pi;
    
    // Фазовий доданок інтерференції між двома щілинами
    double alpha = (pi * cfg.slit_distance * y) / (cfg.wavelength * cfg.screen_dist);
    double interference = std::cos(alpha) * std::cos(alpha);
    
    // Однощілинна дифракція (функція sinc)
    double beta = (pi * cfg.slit_width * y) / (cfg.wavelength * cfg.screen_dist);
    double diffraction = 1.0;
    if (std::abs(beta) > 1e-7) {
        diffraction = std::sin(beta) / beta;
        diffraction *= diffraction;
    }
    
    return interference * diffraction;
}

// Монте-Карло алгоритм генерації попоштучних влучань електронів
std::vector<size_t> run_monte_carlo_electrons(size_t total_electrons, const ExperimentConfig& cfg) {
    std::vector<size_t> histogram(cfg.num_bins, 0);
    
    // Використання 64-бітного випрямленого генератора Вихру Мерсенна
    std::mt19937_64 rng(42); 
    std::uniform_real_distribution<double> dist_y(-cfg.screen_half_width, cfg.screen_half_width);
    std::uniform_real_distribution<double> dist_u(0.0, 1.0);
    
    size_t accepted = 0;
    while (accepted < total_electrons) {
        double y_cand = dist_y(rng);
        double prob = calculate_probability(y_cand, cfg);
        
        // Метод вибірки з відхиленням фон Неймана
        if (dist_u(rng) <= prob) {
            double norm_y = (y_cand + cfg.screen_half_width) / (2.0 * cfg.screen_half_width);
            size_t bin = static_cast<size_t>(norm_y * cfg.num_bins);
            if (bin < cfg.num_bins) {
                histogram[bin]++;
                accepted++;
            }
        }
    }
    
    return histogram;
}

int main() {
    ExperimentConfig cfg;
    const size_t electron_count = 100000;
    
    std::cout << "=== Квантовий Монте-Карло симулятор двохщілинної інтерференції ===\n";
    std::cout << "Параметри: λ_dB = " << cfg.wavelength * 1e9 << " нм, d = " << cfg.slit_distance * 1e6 << " мкм\n";
    std::cout << "Загальна кількість зареєстрованих попоштучних електронів: " << electron_count << "\n\n";
    
    auto histogram = run_monte_carlo_electrons(electron_count, cfg);
    
    std::cout << "Розподіл влучань на детекторі (вертикальна координата y):\n";
    for (size_t i = 0; i < cfg.num_bins; i += 4) {
        double y = -cfg.screen_half_width + (static_cast<double>(i) + 0.5) * (2.0 * cfg.screen_half_width / cfg.num_bins);
        size_t count = histogram[i];
        size_t bar_len = count / 500;
        
        std::cout << (y >= 0 ? " +" : " ") << y * 1000.0 << " мм | ";
        std::cout << std::string(bar_len, '#') << " (" << count << ")\n";
    }
    
    return 0;
}
