// C++ Modern Idiomatic Implementation: RAII, STL Containers & Object-Oriented Design
#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <random>
#include <numeric>
#include <iomanip>

namespace noise {

class WhiteNoiseGenerator {
public:
    WhiteNoiseGenerator(double target_psd_g0, double sampling_rate_hz)
        : rd_(), gen_(rd_()), dist_(0.0, std::sqrt(target_psd_g0 * (sampling_rate_hz / 2.0))) {}

    std::vector<double> generate(std::size_t count) {
        std::vector<double> samples(count);
        for (auto& s : samples) {
            s = dist_(gen_);
        }
        return samples;
    }

private:
    std::random_device rd_;
    std::mt19937 gen_;
    std::normal_distribution<double> dist_;
};

class WelchSpectralAnalyzer {
public:
    explicit WelchSpectralAnalyzer(std::size_t segment_length)
        : seg_len_(segment_length), window_(segment_length) {
        double win_sq_sum = 0.0;
        const double pi = std::acos(-1.0);
        for (std::size_t n = 0; n < seg_len_; ++n) {
            window_[n] = 0.5 * (1.0 - std::cos(2.0 * pi * n / (seg_len_ - 1)));
            win_sq_sum += window_[n] * window_[n];
        }
        win_norm_sq_ = win_sq_sum;
    }

    std::vector<double> compute_psd(const std::vector<double>& signal, double fs_hz) const {
        const std::size_t num_bins = seg_len_ / 2 + 1;
        std::vector<double> psd_accum(num_bins, 0.0);

        const std::size_t step = seg_len_ / 2;
        if (signal.size() < seg_len_) return psd_accum;
        
        const std::size_t num_segments = (signal.size() - seg_len_) / step + 1;

        std::vector<std::complex<double>> buffer(seg_len_);
        for (std::size_t seg = 0; seg < num_segments; ++seg) {
            const std::size_t offset = seg * step;
            for (std::size_t n = 0; n < seg_len_; ++n) {
                buffer[n] = signal[offset + n] * window_[n];
            }

            fft_inplace(buffer);

            for (std::size_t k = 0; k < num_bins; ++k) {
                double mag_sq = std::norm(buffer[k]);
                double scale = (k == 0 || k == seg_len_ / 2) ? 1.0 : 2.0;
                psd_accum[k] += scale * mag_sq / (fs_hz * win_norm_sq_);
            }
        }

        for (auto& val : psd_accum) {
            val /= num_segments;
        }

        return psd_accum;
    }

private:
    static void fft_inplace(std::vector<std::complex<double>>& x) {
        const std::size_t N = x.size();
        if (N <= 1) return;
        
        std::size_t j = 0;
        for (std::size_t i = 0; i < N; ++i) {
            if (i < j) std::swap(x[i], x[j]);
            std::size_t m = N >> 1;
            while (m >= 1 && j >= m) {
                j -= m;
                m >>= 1;
            }
            j += m;
        }
        const double pi = std::acos(-1.0);
        for (std::size_t len = 2; len <= N; len <<= 1) {
            double ang = -2.0 * pi / len;
            std::complex<double> wlen(std::cos(ang), std::sin(ang));
            for (std::size_t i = 0; i < N; i += len) {
                std::complex<double> w(1.0, 0.0);
                for (std::size_t k = 0; k < len / 2; ++k) {
                    std::complex<double> u = x[i + k];
                    std::complex<double> v = x[i + k + len / 2] * w;
                    x[i + k] = u + v;
                    x[i + k + len / 2] = u - v;
                    w *= wlen;
                }
            }
        }
    }

    std::size_t seg_len_;
    std::vector<double> window_;
    double win_norm_sq_;
};

} // namespace noise

int main() {
    constexpr double fs = 10000.0;
    constexpr double target_g0 = 1e-4;
    constexpr std::size_t seg_len = 1024;

    noise::WhiteNoiseGenerator gen(target_g0, fs);
    auto signal = gen.generate(20000);

    noise::WelchSpectralAnalyzer analyzer(seg_len);
    auto psd = analyzer.compute_psd(signal, fs);

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "C++ Welch PSD Estimate (Target: " << target_g0 << " V^2/Hz):\n";
    for (std::size_t i = 0; i < 5; ++i) {
        double freq = i * (fs / seg_len);
        std::cout << "Freq: " << freq << " Hz -> PSD: " << psd[i] << " V^2/Hz\n";
    }

    return 0;
}
