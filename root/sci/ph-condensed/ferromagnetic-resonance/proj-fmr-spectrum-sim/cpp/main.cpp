#include <iostream>
#include <vector>
#include <cmath>
#include <numeric>
#include <stdexcept>
#include <iomanip>

struct FMRResult {
    double alpha;
    double dh0_oe;
};

class FMRAnalyzer {
private:
    double ms_a_m;
    double g_factor;
    double gamma_ghz_t;

public:
    FMRAnalyzer(double ms_ka_m = 800.0, double g = 2.10)
        : ms_a_m(ms_ka_m * 1000.0), g_factor(g) {
        gamma_ghz_t = (g_factor * 1.760859e11) / (2.0 * M_PI * 1e9);
    }

    double calculate_kittel_inplane(double freq_ghz) const {
        double mu0_ms = 4.0 * M_PI * 1e-7 * ms_a_m;
        double f_g = freq_ghz / gamma_ghz_t;
        double b_r = (-mu0_ms + std::sqrt(mu0_ms * mu0_ms + 4.0 * f_g * f_g)) / 2.0;
        return b_r * 10000.0; // Гаус / Ерстед
    }

    FMRResult fit_gilbert(const std::vector<double>& freqs_ghz,
                          const std::vector<double>& linewidths_oe) const {
        size_t n = freqs_ghz.size();
        if (n < 2 || n != linewidths_oe.size()) {
            throw std::invalid_argument("Некоректний розмір вимірювальних масивів");
        }

        double sum_f = 0.0, sum_dh = 0.0, sum_ff = 0.0, sum_fdh = 0.0;
        for (size_t i = 0; i < n; ++i) {
            sum_f += freqs_ghz[i];
            sum_dh += linewidths_oe[i];
            sum_ff += freqs_ghz[i] * freqs_ghz[i];
            sum_fdh += freqs_ghz[i] * linewidths_oe[i];
        }

        double slope = (n * sum_fdh - sum_f * sum_dh) / (n * sum_ff - sum_f * sum_f);
        double dh0 = (sum_dh - slope * sum_f) / static_cast<double>(n);
        double alpha = (slope * gamma_ghz_t) / 2000.0;

        return FMRResult{alpha, dh0};
    }
};

int main() {
    FMRAnalyzer analyzer(800.0, 2.08);
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Резонансне поле на 9.5 ГГц: " 
              << analyzer.calculate_kittel_inplane(9.5) << " Ое\n";

    std::vector<double> freqs = {4.0, 8.0, 12.0, 16.0, 20.0};
    std::vector<double> dhs = {6.2, 8.1, 10.0, 11.9, 13.8};

    try {
        FMRResult res = analyzer.fit_gilbert(freqs, dhs);
        std::cout << "Параметр Гільберта alpha: " << res.alpha << "\n";
        std::cout << "Неоднорідне уширення ΔH0: " << res.dh0_oe << " Ое\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
    }
    return 0;
}
