#include <iostream>
#include <complex>
#include <vector>
#include <array>
#include <random>
#include <cmath>
#include <limits>

using cdouble = std::complex<double>;

constexpr double INV_SQRT2 = 0.7071067811865475;

const std::array<cdouble, 4> QPSK_CONSTELLATION = {
    cdouble( INV_SQRT2,  INV_SQRT2),
    cdouble(-INV_SQRT2,  INV_SQRT2),
    cdouble( INV_SQRT2, -INV_SQRT2),
    cdouble(-INV_SQRT2, -INV_SQRT2)
};

cdouble hard_slice_qpsk(cdouble val) noexcept {
    double re = (val.real() >= 0.0) ? INV_SQRT2 : -INV_SQRT2;
    double im = (val.imag() >= 0.0) ? INV_SQRT2 : -INV_SQRT2;
    return cdouble(re, im);
}

// Аналітичне обернення комплексної матриці 2x2
std::array<cdouble, 4> mat2x2_inv(cdouble a, cdouble b, cdouble c, cdouble d) noexcept {
    cdouble det = a * d - b * c;
    if (std::abs(det) < 1e-12) {
        det = cdouble(1e-12, 0.0);
    }
    cdouble inv_det = cdouble(1.0, 0.0) / det;
    return { d * inv_det, -b * inv_det, -c * inv_det, a * inv_det };
}

// Zero-Forcing детектор
std::array<cdouble, 2> detect_zf(const std::array<std::array<cdouble, 2>, 2>& H,
                                 const std::array<cdouble, 2>& y) noexcept {
    cdouble h11 = H[0][0], h12 = H[0][1];
    cdouble h21 = H[1][0], h22 = H[1][1];

    cdouble g11 = std::conj(h11) * h11 + std::conj(h21) * h21;
    cdouble g12 = std::conj(h11) * h12 + std::conj(h21) * h22;
    cdouble g21 = std::conj(h12) * h11 + std::conj(h22) * h21;
    cdouble g22 = std::conj(h12) * h12 + std::conj(h22) * h22;

    auto [ig11, ig12, ig21, ig22] = mat2x2_inv(g11, g12, g21, g22);

    cdouble ymf1 = std::conj(h11) * y[0] + std::conj(h21) * y[1];
    cdouble ymf2 = std::conj(h12) * y[0] + std::conj(h22) * y[1];

    cdouble x1_est = ig11 * ymf1 + ig12 * ymf2;
    cdouble x2_est = ig21 * ymf1 + ig22 * ymf2;

    return { hard_slice_qpsk(x1_est), hard_slice_qpsk(x2_est) };
}

// MMSE детектор
std::array<cdouble, 2> detect_mmse(const std::array<std::array<cdouble, 2>, 2>& H,
                                   const std::array<cdouble, 2>& y,
                                   double snr_lin) noexcept {
    cdouble h11 = H[0][0], h12 = H[0][1];
    cdouble h21 = H[1][0], h22 = H[1][1];

    double alpha = 1.0 / std::max(snr_lin, 1e-4);

    cdouble g11 = (std::conj(h11) * h11 + std::conj(h21) * h21) + alpha;
    cdouble g12 = std::conj(h11) * h12 + std::conj(h21) * h22;
    cdouble g21 = std::conj(h12) * h11 + std::conj(h22) * h21;
    cdouble g22 = (std::conj(h12) * h12 + std::conj(h22) * h22) + alpha;

    auto [ig11, ig12, ig21, ig22] = mat2x2_inv(g11, g12, g21, g22);

    cdouble ymf1 = std::conj(h11) * y[0] + std::conj(h21) * y[1];
    cdouble ymf2 = std::conj(h12) * y[0] + std::conj(h22) * y[1];

    cdouble x1_est = ig11 * ymf1 + ig12 * ymf2;
    cdouble x2_est = ig21 * ymf1 + ig22 * ymf2;

    return { hard_slice_qpsk(x1_est), hard_slice_qpsk(x2_est) };
}

// Maximum Likelihood (ML) детектор
std::array<cdouble, 2> detect_ml(const std::array<std::array<cdouble, 2>, 2>& H,
                                 const std::array<cdouble, 2>& y) noexcept {
    cdouble h11 = H[0][0], h12 = H[0][1];
    cdouble h21 = H[1][0], h22 = H[1][1];

    double best_dist = std::numeric_limits<double>::infinity();
    std::array<cdouble, 2> best_s = { QPSK_CONSTELLATION[0], QPSK_CONSTELLATION[0] };

    for (const auto& s1 : QPSK_CONSTELLATION) {
        for (const auto& s2 : QPSK_CONSTELLATION) {
            cdouble r1 = h11 * s1 + h12 * s2;
            cdouble r2 = h21 * s1 + h22 * s2;

            double dist = std::norm(y[0] - r1) + std::norm(y[1] - r2);
            if (dist < best_dist) {
                best_dist = dist;
                best_s = { s1, s2 };
            }
        }
    }
    return best_s;
}

int main() {
    std::mt19937 rng(42);
    std::normal_distribution<double> dist_norm(0.0, INV_SQRT2);
    std::uniform_int_distribution<int> dist_sym(0, 3);

    const int num_packets = 10000;
    const double snr_db = 14.0;
    const double snr_lin = std::pow(10.0, snr_db / 10.0);
    const double sigma_noise = std::sqrt(1.0 / (2.0 * snr_lin));
    std::normal_distribution<double> dist_noise(0.0, sigma_noise);

    int err_zf = 0, err_mmse = 0, err_ml = 0;

    for (int p = 0; p < num_packets; ++p) {
        std::array<cdouble, 2> tx_syms = {
            QPSK_CONSTELLATION[dist_sym(rng)],
            QPSK_CONSTELLATION[dist_sym(rng)]
        };

        std::array<std::array<cdouble, 2>, 2> H = {{
            { cdouble(dist_norm(rng), dist_norm(rng)), cdouble(dist_norm(rng), dist_norm(rng)) },
            { cdouble(dist_norm(rng), dist_norm(rng)), cdouble(dist_norm(rng), dist_norm(rng)) }
        }};

        cdouble n1(dist_noise(rng), dist_noise(rng));
        cdouble n2(dist_noise(rng), dist_noise(rng));

        std::array<cdouble, 2> y = {
            H[0][0] * tx_syms[0] + H[0][1] * tx_syms[1] + n1,
            H[1][0] * tx_syms[0] + H[1][1] * tx_syms[1] + n2
        };

        auto hat_zf = detect_zf(H, y);
        auto hat_mmse = detect_mmse(H, y, snr_lin);
        auto hat_ml = detect_ml(H, y);

        for (int i = 0; i < 2; ++i) {
            if (std::abs(hat_zf[i] - tx_syms[i]) > 1e-4) ++err_zf;
            if (std::abs(hat_mmse[i] - tx_syms[i]) > 1e-4) ++err_mmse;
            if (std::abs(hat_ml[i] - tx_syms[i]) > 1e-4) ++err_ml;
        }
    }

    const double total_syms = num_packets * 2.0;
    std::cout << "Результати 2x2 MIMO симуляції (SNR = " << snr_db << " dB):\n";
    std::cout << "  ZF SER:   " << (err_zf / total_syms) << "\n";
    std::cout << "  MMSE SER: " << (err_mmse / total_syms) << "\n";
    std::cout << "  ML SER:   " << (err_ml / total_syms) << "\n";

    return 0;
}
