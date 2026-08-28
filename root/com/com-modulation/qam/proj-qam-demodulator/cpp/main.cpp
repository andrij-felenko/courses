#include <iostream>
#include <vector>
#include <complex>
#include <random>
#include <cmath>
#include <iomanip>
#include <span>

class QamModem16 {
public:
    using Complex = std::complex<double>;

    explicit QamModem16()
        : norm_(1.0 / std::sqrt(10.0)) {}

    [[nodiscard]] std::vector<Complex> modulate(std::span<const uint8_t> bits) const {
        if (bits.size() % 4 != 0) {
            throw std::invalid_argument("Кількість бітів має бути кратна 4 для 16-QAM");
        }
        size_t num_symbols = bits.size() / 4;
        std::vector<Complex> symbols(num_symbols);

        for (size_t k = 0; k < num_symbols; ++k) {
            uint8_t b_i = (bits[4 * k + 0] << 1) | bits[4 * k + 1];
            uint8_t b_q = (bits[4 * k + 2] << 1) | bits[4 * k + 3];

            double i_val = grayMap2Bit(b_i) * norm_;
            double q_val = grayMap2Bit(b_q) * norm_;
            symbols[k] = {i_val, q_val};
        }
        return symbols;
    }

    [[nodiscard]] std::vector<uint8_t> demapHard(std::span<const Complex> symbols) const {
        double scale = std::sqrt(10.0);
        std::vector<uint8_t> bits(symbols.size() * 4);

        for (size_t k = 0; k < symbols.size(); ++k) {
            double val_i = symbols[k].real() * scale;
            double val_q = symbols[k].imag() * scale;

            uint8_t b_i = grayDemap2Bit(val_i);
            uint8_t b_q = grayDemap2Bit(val_q);

            bits[4 * k + 0] = (b_i >> 1) & 0x01;
            bits[4 * k + 1] = (b_i >> 0) & 0x01;
            bits[4 * k + 2] = (b_q >> 1) & 0x01;
            bits[4 * k + 3] = (b_q >> 0) & 0x01;
        }
        return bits;
    }

    [[nodiscard]] std::vector<double> demapSoftMaxLog(std::span<const Complex> symbols, double n0) const {
        double d = 2.0 * norm_;
        double factor = 2.0 * d / (n0 / 2.0);
        std::vector<double> llrs(symbols.size() * 4);

        for (size_t k = 0; k < symbols.size(); ++k) {
            double yi = symbols[k].real();
            double yq = symbols[k].imag();

            llrs[4 * k + 0] = factor * yi;
            llrs[4 * k + 1] = factor * (d - std::abs(yi));
            llrs[4 * k + 2] = factor * yq;
            llrs[4 * k + 3] = factor * (d - std::abs(yq));
        }
        return llrs;
    }

private:
    double norm_;

    static double grayMap2Bit(uint8_t b) {
        switch (b & 0x03) {
            case 0: return -3.0;
            case 1: return -1.0;
            case 3: return  1.0;
            case 2: return  3.0;
            default: return 0.0;
        }
    }

    static uint8_t grayDemap2Bit(double v) {
        if (v < -2.0)      return 0;
        else if (v < 0.0)  return 1;
        else if (v < 2.0)  return 3;
        else               return 2;
    }
};

int main() {
    constexpr size_t num_bits = 40000;
    std::mt19937 rng(42);
    std::uniform_int_distribution<int> bit_dist(0, 1);

    std::vector<uint8_t> tx_bits(num_bits);
    for (auto &b : tx_bits) b = static_cast<uint8_t>(bit_dist(rng));

    QamModem16 modem;
    auto tx_symbols = modem.modulate(tx_bits);

    std::cout << "=== C++17 16-QAM Modem Simulation ===\n";
    std::cout << std::fixed << std::setprecision(5);
    std::cout << "Eb/N0 (dB) | BER (Hard)  | BER (Soft Sign)\n";
    std::cout << "-------------------------------------------\n";

    for (double ebn0_db = 0.0; ebn0_db <= 12.0; ebn0_db += 2.0) {
        double ebn0_lin = std::pow(10.0, ebn0_db / 10.0);
        double esn0_lin = 4.0 * ebn0_lin;
        double n0 = 1.0 / esn0_lin;
        double sigma = std::sqrt(n0 / 2.0);

        std::normal_distribution<double> noise_dist(0.0, sigma);
        std::vector<std::complex<double>> rx_symbols(tx_symbols.size());

        for (size_t i = 0; i < tx_symbols.size(); ++i) {
            rx_symbols[i] = tx_symbols[i] + std::complex<double>(noise_dist(rng), noise_dist(rng));
        }

        auto rx_bits = modem.demapHard(rx_symbols);
        auto llrs = modem.demapSoftMaxLog(rx_symbols, n0);

        size_t hard_errors = 0;
        size_t soft_errors = 0;
        for (size_t i = 0; i < num_bits; ++i) {
            if (rx_bits[i] != tx_bits[i]) hard_errors++;
            uint8_t soft_bit = (llrs[i] >= 0.0) ? 1 : 0;
            if (soft_bit != tx_bits[i]) soft_errors++;
        }

        std::cout << " " << std::setw(4) << std::setprecision(1) << ebn0_db
                  << " dB   | " << std::setprecision(5) << static_cast<double>(hard_errors) / num_bits
                  << "     | " << static_cast<double>(soft_errors) / num_bits << "\n";
    }

    return 0;
}
