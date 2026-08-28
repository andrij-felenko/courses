#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <random>
#include <algorithm>
#include <numeric>

class CssModemSim {
public:
    using Complex = std::complex<double>;

    CssModemSim(int spreading_factor, double snr_db)
        : sf_(spreading_factor),
          size_(1 << spreading_factor),
          snr_db_(snr_db),
          gen_(1337) {}

    std::vector<Complex> generate_upchirp(int symbol) const {
        std::vector<Complex> chirp(size_);
        const double pi = std::acos(-1.0);
        for (int n = 0; n < size_; ++n) {
            int idx = (n + symbol) % size_;
            double phase = pi * static_cast<double>(idx * idx) / static_cast<double>(size_);
            chirp[n] = std::polar(1.0, phase);
        }
        return chirp;
    }

    std::vector<Complex> generate_downchirp() const {
        std::vector<Complex> chirp(size_);
        const double pi = std::acos(-1.0);
        for (int n = 0; n < size_; ++n) {
            double phase = -pi * static_cast<double>(n * n) / static_cast<double>(size_);
            chirp[n] = std::polar(1.0, phase);
        }
        return chirp;
    }

    std::vector<Complex> add_awgn(const std::vector<Complex>& input) {
        std::vector<Complex> noisy = input;
        double snr_linear = std::pow(10.0, snr_db_ / 10.0);
        double stddev = std::sqrt(1.0 / (2.0 * snr_linear));
        std::normal_distribution<double> dist(0.0, stddev);

        for (auto& sample : noisy) {
            sample += Complex(dist(gen_), dist(gen_));
        }
        return noisy;
    }

    int decode(const std::vector<Complex>& received) const {
        auto down_chirp = generate_downchirp();
        std::vector<Complex> dechirped(size_);

        for (size_t i = 0; i < size_; ++i) {
            dechirped[i] = received[i] * down_chirp[i];
        }

        std::vector<double> dft_magnitudes(size_, 0.0);
        const double pi = std::acos(-1.0);

        for (int k = 0; k < size_; ++k) {
            Complex sum(0.0, 0.0);
            for (int n = 0; n < size_; ++n) {
                double angle = -2.0 * pi * k * n / static_cast<double>(size_);
                sum += dechirped[n] * std::polar(1.0, angle);
            }
            dft_magnitudes[k] = std::abs(sum);
        }

        auto max_it = std::max_element(dft_magnitudes.begin(), dft_magnitudes.end());
        return static_cast<int>(std::distance(dft_magnitudes.begin(), max_it));
    }

private:
    int sf_;
    int size_;
    double snr_db_;
    mutable std::mt19937 gen_;
};

int main() {
    int sf = 8;
    int symbol_tx = 105;
    double snr_db = -12.0;

    CssModemSim modem(sf, snr_db);

    auto tx_signal = modem.generate_upchirp(symbol_tx);
    auto rx_signal = modem.add_awgn(tx_signal);
    int symbol_rx = modem.decode(rx_signal);

    std::cout << "=== МОДЕЛЮВАННЯ LoRa CSS (Мова C++) ===\n";
    std::cout << "Spreading Factor: " << sf << " (N = " << (1 << sf) << ")\n";
    std::cout << "Переданий символ: " << symbol_tx << "\n";
    std::cout << "Вхідний SNR:      " << snr_db << " dB\n";
    std::cout << "Декодовано:       " << symbol_rx << "\n";

    if (symbol_rx == symbol_tx) {
        std::cout << "РЕЗУЛЬТАТ: УСПІШНО ДЕКОДОВАНО У ГАУСОВОМУ ШУМІ!\n";
    } else {
        std::cout << "РЕЗУЛЬТАТ: ПОМИЛКА ДЕКОДУВАННЯ\n";
    }

    return 0;
}
