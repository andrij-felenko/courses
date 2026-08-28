#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <algorithm>

struct PolaritonSpectrumResult {
    std::vector<double> h_array;
    std::vector<double> f_array;
    std::vector<double> f_lmp;
    std::vector<double> f_ump;
    std::vector<std::vector<double>> s21_matrix;
    double rabi_mhz;
};

PolaritonSpectrumResult compute_polariton_spectrum_cpp(
    double f_a = 10.0e9,
    double kappa_tot = 3.0e6,
    double kappa_ext = 1.5e6,
    double gamma_m = 1.0e6,
    double g_eff = 150.0e6,
    double gamma_e = 28.0e9,
    double h_min = 0.34,
    double h_max = 0.37,
    size_t num_h = 250,
    size_t num_f = 400
) {
    PolaritonSpectrumResult result;
    result.h_array.resize(num_h);
    result.f_array.resize(num_f);
    result.f_lmp.resize(num_h);
    result.f_ump.resize(num_h);
    result.s21_matrix.assign(num_f, std::vector<double>(num_h, 0.0));

    double dh = (h_max - h_min) / static_cast<double>(num_h - 1);
    for (size_t j = 0; j < num_h; ++j) {
        result.h_array[j] = h_min + static_cast<double>(j) * dh;
    }

    double f_start = f_a - 3.5 * g_eff;
    double f_end = f_a + 3.5 * g_eff;
    double df = (f_end - f_start) / static_cast<double>(num_f - 1);
    for (size_t i = 0; i < num_f; ++i) {
        result.f_array[i] = f_start + static_cast<double>(i) * df;
    }

    const std::complex<double> I(0.0, 1.0);
    const double kappa_hz = kappa_tot / (2.0 * M_PI);
    const double gamma_hz = gamma_m / (2.0 * M_PI);
    const double g_hz = g_eff / (2.0 * M_PI);
    const double k_ext_hz = kappa_ext / (2.0 * M_PI);

    size_t res_idx = 0;
    double min_delta = 1.0e18;

    for (size_t j = 0; j < num_h; ++j) {
        double f_m = gamma_e * result.h_array[j];
        if (std::abs(f_m - f_a) < min_delta) {
            min_delta = std::abs(f_m - f_a);
            res_idx = j;
        }

        // Аналітичне розв'язання квадратного рівняння для 2x2 матриці H_eff:
        // (f_a - i*kappa - lambda) * (f_m - i*gamma - lambda) - g^2 = 0
        std::complex<double> h11 = f_a - I * kappa_hz;
        std::complex<double> h22 = f_m - I * gamma_hz;
        std::complex<double> tr = h11 + h22;
        std::complex<double> det = h11 * h22 - g_hz * g_hz;
        std::complex<double> disc = std::sqrt(tr * tr - 4.0 * det);

        std::complex<double> lambda1 = 0.5 * (tr - disc);
        std::complex<double> lambda2 = 0.5 * (tr + disc);

        double r1 = lambda1.real();
        double r2 = lambda2.real();

        result.f_lmp[j] = std::min(r1, r2);
        result.f_ump[j] = std::max(r1, r2);

        // Обчислення проходження S21
        for (size_t i = 0; i < num_f; ++i) {
            double f_val = result.f_array[i];
            std::complex<double> denom_m = f_val - f_m + I * gamma_hz;
            std::complex<double> denom_tot = (f_val - f_a + I * kappa_hz) - (g_hz * g_hz) / denom_m;
            std::complex<double> s21 = (-I * k_ext_hz) / denom_tot;
            result.s21_matrix[i][j] = std::abs(s21);
        }
    }

    result.rabi_mhz = (result.f_ump[res_idx] - result.f_lmp[res_idx]) / 1.0e6;
    return result;
}

int main() {
    auto res = compute_polariton_spectrum_cpp();
    std::cout << "C++ розраховане розщеплення Рабі: " << res.rabi_mhz << " МГц\n";
    return 0;
}
