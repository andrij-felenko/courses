#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <iomanip>
#include <numeric>
#include <span>

// Вітка ряду Проні (елемент Максвелла)
struct PronyElement {
    double G_i;    // Модуль зсуву (Па)
    double tau_i;  // Час релаксації (с)
    double h_i{0.0}; // Внутрішній стан напруження (Па)
};

// Результат обчислення DMA
struct DMAResult {
    double storage_modulus; // G' (Па)
    double loss_modulus;    // G'' (Па)
    double loss_tangent;    // tan(delta)
    std::complex<double> complex_modulus; // G* = G' + i G''
};

class ViscoelasticModel {
private:
    double G_inf_; // Тривалий рівноважний модуль (Па)
    std::vector<PronyElement> elements_;

public:
    ViscoelasticModel(double G_inf, std::span<const double> G_i, std::span<const double> tau_i)
        : G_inf_(G_inf) {
        if (G_i.size() != tau_i.size()) {
            throw std::invalid_argument("Масиви G_i та tau_i повинні мати однакову довжину!");
        }
        elements_.reserve(G_i.size());
        for (size_t i = 0; i < G_i.size(); ++i) {
            elements_.push_back({G_i[i], tau_i[i], 0.0});
        }
    }

    // Очищення внутрішніх змінних стану
    void reset_state() noexcept {
        for (auto& elem : elements_) {
            elem.h_i = 0.0;
        }
    }

    // Аналітичний модуль релаксації G(t)
    [[nodiscard]] double relaxation_modulus(double t) const noexcept {
        double G_t = G_inf_;
        for (const auto& elem : elements_) {
            G_t += elem.G_i * std::exp(-t / elem.tau_i);
        }
        return G_t;
    }

    // Чисельний приріст напруження при заданому кроці деформації d_gamma за час dt
    double step_strain(double d_gamma, double dt) noexcept {
        double total_stress = G_inf_ * d_gamma;
        for (auto& elem : elements_) {
            double exp_factor = std::exp(-dt / elem.tau_i);
            elem.h_i = elem.h_i * exp_factor + elem.G_i * d_gamma * exp_factor;
            total_stress += elem.h_i;
        }
        return total_stress;
    }

    // Динамічний механічний аналіз (DMA) на круговій частоті omega (рад/с)
    [[nodiscard]] DMAResult compute_dma(double omega) const noexcept {
        double G_prime = G_inf_;
        double G_double_prime = 0.0;

        for (const auto& elem : elements_) {
            double w_tau = omega * elem.tau_i;
            double w_tau_sq = w_tau * w_tau;
            double denom = 1.0 + w_tau_sq;

            G_prime        += elem.G_i * (w_tau_sq / denom);
            G_double_prime += elem.G_i * (w_tau / denom);
        }

        double tan_delta = (G_prime > 1e-12) ? (G_double_prime / G_prime) : 0.0;
        return {G_prime, G_double_prime, tan_delta, {G_prime, G_double_prime}};
    }
};

int main() {
    try {
        // Налаштування матеріалу (ПЕНП / НДПЕ поліетилен при 20 °C)
        double G_inf = 8.0e7; // 80 МПа
        std::vector<double> G_i   = {4.0e8, 2.5e8, 1.0e8};
        std::vector<double> tau_i = {0.05,  0.5,   5.0};

        ViscoelasticModel model(G_inf, G_i, tau_i);

        std::cout << std::fixed << std::setprecision(2);
        std::cout << "=== 1. РЕЛАКСАЦІЯ НАПРУЖЕНЬ G(t) (C++) ===\n";
        std::cout << "t (c)    | G(t) (МПа)   | Відсоток початкового\n";
        std::cout << "----------------------------------------------\n";

        double G_0 = model.relaxation_modulus(0.0);
        for (double t = 0.0; t <= 10.0; t += 1.0) {
            double G_t = model.relaxation_modulus(t);
            std::cout << std::setw(6) << t << "   | "
                      << std::setw(12) << G_t / 1.0e6 << " | "
                      << std::setw(18) << (G_t / G_0) * 100.0 << "%\n";
        }

        std::cout << "\n=== 2. ДИНАМІЧНИЙ СПЕКТР DMA (C++) ===\n";
        std::cout << "w (рад/с) | G' (МПа)    | G'' (МПа)   | tan(delta)\n";
        std::cout << "---------------------------------------------------\n";

        std::vector<double> frequencies = {0.01, 0.1, 1.0, 10.0, 100.0};
        for (double w : frequencies) {
            auto dma = model.compute_dma(w);
            std::cout << std::setw(9) << w << " | "
                      << std::setw(11) << dma.storage_modulus / 1.0e6 << " | "
                      << std::setw(11) << dma.loss_modulus / 1.0e6 << " | "
                      << std::setw(10) << std::setprecision(4) << dma.loss_tangent << "\n"
                      << std::setprecision(2);
        }
    } catch (const std::exception& ex) {
        std::cerr << "Виняток: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
