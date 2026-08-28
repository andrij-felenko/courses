#include <cmath>
#include <complex>
#include <numbers>
#include <span>
#include <utility>

// FFT «на місці» над послідовністю комплексних відліків; n = data.size() (степінь двійки)
void fft_radix2(std::span<std::complex<float>> data)
{
    const size_t n = data.size();
    // 1. перестановка за оберненими бітами
    for (size_t i = 1, j = 0; i < n; ++i) {
        size_t bit = n >> 1;
        for (; j & bit; bit >>= 1)
            j ^= bit;
        j ^= bit;
        if (i < j)
            std::swap(data[i], data[j]);
    }
    // 2. log2(n) ярусів метеликів
    for (size_t len = 2; len <= n; len <<= 1) {
        const float ang = -2.0f * std::numbers::pi_v<float> / static_cast<float>(len);
        const std::complex<float> wlen(std::cos(ang), std::sin(ang));
        for (size_t i = 0; i < n; i += len) {
            std::complex<float> w(1.0f, 0.0f);
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
