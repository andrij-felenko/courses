#include <vector>
#include <complex>
#include <cmath>
#include <cstdint>
#include <algorithm>
#include <span>
#include <numbers>
#include <limits>

class SoftDemapper {
public:
    explicit SoftDemapper(double noise_variance)
        : sigma2_(std::max(noise_variance, 1e-12)) {}

    // LLR для BPSK з додаванням апріорної інформації
    [[nodiscard]] std::vector<double> demap_bpsk(
        std::span<const double> rx_symbols,
        std::span<const double> prior_llr = {}) const 
    {
        const double scale = 2.0 / sigma2_;
        std::vector<double> post_llr(rx_symbols.size());

        for (size_t i = 0; i < rx_symbols.size(); ++i) {
            double prior = (i < prior_llr.size()) ? prior_llr[i] : 0.0;
            post_llr[i] = rx_symbols[i] * scale + prior;
        }
        return post_llr;
    }

    // LLR для QPSK (карта Грея)
    [[nodiscard]] std::vector<double> demap_qpsk(
        std::span<const std::complex<double>> rx_symbols) const 
    {
        const double scale = 2.0 * std::numbers::sqrt2 / sigma2_;
        std::vector<double> bit_llrs;
        bit_llrs.reserve(rx_symbols.size() * 2);

        for (const auto& sym : rx_symbols) {
            bit_llrs.push_back(sym.real() * scale);
            bit_llrs.push_back(sym.imag() * scale);
        }
        return bit_llrs;
    }

    // LLR для 16-QAM (Max-Log наближення, карта Грея)
    [[nodiscard]] std::vector<double> demap_16qam_maxlog(
        std::span<const std::complex<double>> rx_symbols) const 
    {
        constexpr double sqrt10 = 3.1622776601683795;
        const double c1 = 4.0 * sqrt10 / sigma2_;
        const double c2 = 2.0 * sqrt10 / sigma2_;
        const double threshold = 2.0 / sqrt10;

        std::vector<double> bit_llrs;
        bit_llrs.reserve(rx_symbols.size() * 4);

        for (const auto& sym : rx_symbols) {
            const double yi = sym.real();
            const double yq = sym.imag();

            bit_llrs.push_back(c1 * yi);
            bit_llrs.push_back(c2 * (threshold - std::abs(yi)));
            bit_llrs.push_back(c1 * yq);
            bit_llrs.push_back(c2 * (threshold - std::abs(yq)));
        }
        return bit_llrs;
    }

    // Вузол перевірки парності Min-Sum LDPC
    [[nodiscard]] static std::vector<double> min_sum_check_node(
        std::span<const double> l_in) 
    {
        if (l_in.size() < 2) return {};

        int global_sign = 1;
        double min1 = std::numeric_limits<double>::max();
        double min2 = std::numeric_limits<double>::max();
        size_t min1_idx = 0;

        for (size_t i = 0; i < l_in.size(); ++i) {
            if (l_in[i] < 0.0) {
                global_sign = -global_sign;
            }
            double abs_val = std::abs(l_in[i]);
            if (abs_val < min1) {
                min2 = min1;
                min1 = abs_val;
                min1_idx = i;
            } else if (abs_val < min2) {
                min2 = abs_val;
            }
        }

        std::vector<double> l_ext(l_in.size());
        for (size_t i = 0; i < l_in.size(); ++i) {
            int edge_sign = (l_in[i] < 0.0) ? -global_sign : global_sign;
            double min_mag = (i == min1_idx) ? min2 : min1;
            l_ext[i] = static_cast<double>(edge_sign) * min_mag;
        }
        return l_ext;
    }

    // 8-бітна квантизація LLR для апаратного декодера
    [[nodiscard]] static int8_t quantize(double llr, double scale_factor) {
        double val = std::round(llr * scale_factor);
        return static_cast<int8_t>(std::clamp(val, -127.0, 127.0));
    }

private:
    double sigma2_;
};
