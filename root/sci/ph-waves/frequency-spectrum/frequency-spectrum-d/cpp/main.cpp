#include <iostream>
#include <vector>
#include <complex>
#include <numbers>
#include <span>
#include <cmath>
#include <algorithm>
#include <memory>

struct SpectrumResult {
    std::vector<double> freqs;
    std::vector<double> magnitudes;
    std::vector<double> phases;
    double fundamental_freq{0.0};
    double thd_percent{0.0};
};

class SpectrumAnalyzer {
public:
    explicit SpectrumAnalyzer(size_t fft_size) : size_(fft_size) {
        if ((size_ & (size_ - 1)) != 0 || size_ == 0) {
            throw std::invalid_argument("FFT size must be a power of two");
        }
        precompute_window();
    }

    [[nodiscard]] SpectrumResult analyze(std::span<const double> signal, double sample_rate) const {
        if (signal.size() < size_) {
            throw std::invalid_argument("Signal size is smaller than analyzer FFT size");
        }

        std::vector<std::complex<double>> buffer(size_);
        for (size_t i = 0; i < size_; ++i) {
            buffer[i] = signal[i] * window_[i];
        }

        fft_in_place(buffer);

        const size_t num_bins = size_ / 2 + 1;
        SpectrumResult result;
        result.freqs.resize(num_bins);
        result.magnitudes.resize(num_bins);
        result.phases.resize(num_bins);

        const double df = sample_rate / static_cast<double>(size_);
        size_t peak_bin = 1;
        double max_mag = 0.0;

        for (size_t k = 0; k < num_bins; ++k) {
            result.freqs[k] = static_cast<double>(k) * df;
            double mag = 2.0 * std::abs(buffer[k]) / window_sum_;
            if (k == 0 || k == size_ / 2) {
                mag /= 2.0;
            }

            result.magnitudes[k] = mag;
            result.phases[k] = std::arg(buffer[k]);

            if (k > 0 && k < size_ / 2 && mag > max_mag) {
                max_mag = mag;
                peak_bin = k;
            }
        }

        result.fundamental_freq = static_cast<double>(peak_bin) * df;

        // Обчислення коефіцієнта гармонік THD для гармонік 2..10
        double harm_energy = 0.0;
        for (size_t h = 2; h <= 10; ++h) {
            if (const size_t h_bin = h * peak_bin; h_bin < num_bins) {
                harm_energy += result.magnitudes[h_bin] * result.magnitudes[h_bin];
            }
        }
        result.thd_percent = (max_mag > 1e-9) ? (std::sqrt(harm_energy) / max_mag) * 100.0 : 0.0;

        return result;
    }

private:
    size_t size_;
    std::vector<double> window_;
    double window_sum_{0.0};

    void precompute_window() {
        window_.resize(size_);
        window_sum_ = 0.0;
        for (size_t i = 0; i < size_; ++i) {
            // Вікно Ганна
            window_[i] = 0.5 * (1.0 - std::cos(2.0 * std::numbers::pi * static_cast<double>(i) / static_cast<double>(size_ - 1)));
            window_sum_ += window_[i];
        }
    }

    static void fft_in_place(std::span<std::complex<double>> data) {
        const size_t n = data.size();
        // 1. Біт-реверсивна перестановка
        for (size_t i = 1, j = 0; i < n; ++i) {
            size_t bit = n >> 1;
            for (; j & bit; bit >>= 1) {
                j ^= bit;
            }
            j ^= bit;
            if (i < j) {
                std::swap(data[i], data[j]);
            }
        }

        // 2. Яруси метеликів
        for (size_t len = 2; len <= n; len <<= 1) {
            const double ang = -2.0 * std::numbers::pi / static_cast<double>(len);
            const std::complex<double> wlen(std::cos(ang), std::sin(ang));
            for (size_t i = 0; i < n; i += len) {
                std::complex<double> w(1.0, 0.0);
                for (size_t k = 0; k < len / 2; ++k) {
                    const size_t p = i + k;
                    const size_t q = p + len / 2;
                    const auto u = data[p];
                    const auto v = data[q] * w;
                    data[p] = u + v;
                    data[q] = u - v;
                    w *= wlen;
                }
            }
        }
    }
};
