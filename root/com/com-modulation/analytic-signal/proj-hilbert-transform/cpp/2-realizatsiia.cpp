#include <iostream>
#include <vector>
#include <complex>
#include <numbers>
#include <cmath>
#include <span>
#include <expected>
#include <iomanip>

enum class SignalError {
    InvalidSize,
    NullPointer
};

class AnalyticSignalCalculator {
public:
    using Complex = std::complex<double>;

    // Перевірка чи є розмір буфера степенем двійки
    static constexpr bool is_power_of_two(std::size_t n) noexcept {
        return n > 0 && (n & (n - 1)) == 0;
    }

    // Спектральний алгоритм Марпла обчислення аналітичного сигналу
    static std::expected<std::vector<Complex>, SignalError> 
    compute(std::span<const double> input) {
        const std::size_t n = input.size();
        if (!is_power_of_two(n)) {
            return std::unexpected(SignalError::InvalidSize);
        }

        std::vector<Complex> z(n);
        for (std::size_t i = 0; i < n; ++i) {
            z[i] = Complex(input[i], 0.0);
        }

        // 1. Пряме ШВФ
        fft_radix2(z, false);

        // 2. Модифікація спектра H[k]
        const std::size_t half = n / 2;
        for (std::size_t k = 1; k < half; ++k) {
            z[k] *= 2.0; // Подвоєння додатних частот
        }
        for (std::size_t k = half + 1; k < n; ++k) {
            z[k] = Complex(0.0, 0.0); // Обнулення від'ємних частот
        }

        // 3. Зворотне ШВФ
        fft_radix2(z, true);

        return z;
    }

private:
    static void fft_radix2(std::span<Complex> buf, bool inverse) {
        const std::size_t n = buf.size();

        // Перестановка бітів (Bit-reversal)
        std::size_t j = 0;
        for (std::size_t i = 0; i < n; ++i) {
            if (i < j) {
                std::swap(buf[i], buf[j]);
            }
            std::size_t m = n >> 1;
            while (m >= 1 && j >= m) {
                j -= m;
                m >>= 1;
            }
            j += m;
        }

        // Обчислення каскадів метеликів
        for (std::size_t len = 2; len <= n; len <<= 1) {
            const double angle = (inverse ? 2.0 : -2.0) * std::numbers::pi / static_cast<double>(len);
            const Complex wlen = std::polar(1.0, angle);

            for (std::size_t i = 0; i < n; i += len) {
                Complex w(1.0, 0.0);
                for (std::size_t k = 0; k < len / 2; ++k) {
                    Complex u = buf[i + k];
                    Complex v = buf[i + k + len / 2] * w;
                    buf[i + k] = u + v;
                    buf[i + k + len / 2] = u - v;
                    w *= wlen;
                }
            }
        }

        if (inverse) {
            const double inv_n = 1.0 / static_cast<double>(n);
            for (auto& val : buf) {
                val *= inv_n;
            }
        }
    }
};

int main() {
    constexpr std::size_t N = 16;
    std::vector<double> signal(N);

    for (std::size_t i = 0; i < N; ++i) {
        signal[i] = std::cos(2.0 * std::numbers::pi * 2.0 * static_cast<double>(i) / static_cast<double>(N));
    }

    auto result = AnalyticSignalCalculator::compute(signal);
    if (result) {
        std::cout << std::fixed << std::setprecision(4);
        std::cout << "Index\tReal (x)\tImag (x_hat)\tEnvelope (A)\n";
        std::cout << "-----------------------------------------------------\n";
        for (std::size_t i = 0; i < N; ++i) {
            const auto& z = (*result)[i];
            std::cout << i << "\t" 
                      << (z.real() >= 0 ? " " : "") << z.real() << "\t"
                      << (z.imag() >= 0 ? " " : "") << z.imag() << "\t"
                      << std::abs(z) << "\n";
        }
    } else {
        std::cerr << "Помилка обчислення аналітичного сигналу!\n";
    }

    return 0;
}
