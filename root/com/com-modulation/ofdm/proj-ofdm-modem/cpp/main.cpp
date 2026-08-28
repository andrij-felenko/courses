#include <complex>
#include <vector>
#include <cmath>
#include <algorithm>

constexpr int N = 64;                             // піднесних = розмір FFT

// ШПФ Кулі–Тьюкі над контейнером std::vector<std::complex<double>>
static void fft_cpp(std::vector<std::complex<double>>& x, bool inv) {
    int n = static_cast<int>(x.size());
    for (int i = 1, j = 0; i < n; i++) {
        int bit = n >> 1;
        for (; j & bit; bit >>= 1) j ^= bit;
        j |= bit;
        if (i < j) std::swap(x[i], x[j]);
    }
    for (int len = 2; len <= n; len <<= 1) {
        double ang = (inv ? 2.0 : -2.0) * M_PI / len;
        std::complex<double> wl(std::cos(ang), std::sin(ang));
        for (int st = 0; st < n; st += len) {
            std::complex<double> w(1.0, 0.0);
            for (int k = 0; k < len / 2; k++) {
                std::complex<double> u = x[st + k], v = x[st + k + len / 2] * w;
                x[st + k] = u + v;
                x[st + k + len / 2] = u - v;
                w *= wl;
            }
        }
    }
    if (inv) {
        for (auto& v : x) v /= static_cast<double>(n);
    }
}

// Передавач: 2N біт → вектор відліків із префіксом
std::vector<std::complex<double>> tx_cpp(const std::vector<int>& bits, int L) {
    std::vector<std::complex<double>> S(N);
    for (int k = 0; k < N; k++) {
        S[k] = std::complex<double>(1 - 2*bits[2*k], 1 - 2*bits[2*k+1]) / std::sqrt(2.0);
    }
    fft_cpp(S, true);                                      // IFFT
    double scale = std::sqrt(static_cast<double>(N));
    for (auto& v : S) v *= scale;

    std::vector<std::complex<double>> block;
    block.reserve(L + N);
    block.insert(block.end(), S.end() - L, S.end());       // хвіст → у префікс
    block.insert(block.end(), S.begin(), S.end());
    return block;
}

// Приймач: вектор відліків → 2N біт (zero-forcing equalization)
std::vector<int> rx_cpp(const std::vector<std::complex<double>>& block, int L,
                        const std::vector<std::complex<double>>& H) {
    std::vector<std::complex<double>> Y(block.begin() + L, block.begin() + L + N);
    fft_cpp(Y, false);                                     // FFT
    double scale = 1.0 / std::sqrt(static_cast<double>(N));
    std::vector<int> bits(2 * N);
    for (int k = 0; k < N; k++) {
        std::complex<double> Sh = (Y[k] * scale) / H[k];
        bits[2 * k]     = (Sh.real() < 0.0) ? 1 : 0;
        bits[2 * k + 1] = (Sh.imag() < 0.0) ? 1 : 0;
    }
    return bits;
}
