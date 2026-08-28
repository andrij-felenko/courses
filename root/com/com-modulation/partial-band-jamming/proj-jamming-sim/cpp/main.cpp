#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <numeric>
#include <iomanip>
#include <memory>

namespace jamming_sim {

constexpr int NUM_CHANNELS = 64;
constexpr int TOTAL_BITS = 24000;
constexpr int INTERLEAVER_ROWS = 8;
constexpr int INTERLEAVER_COLS = 9;

// ООП-модель FHSS каналу із заданими параметрами шуму й завади
class FhssChannelSimulator {
public:
    FhssChannelSimulator(double clean_snr_db, double jam_snr_db, double rho, uint32_t seed = 1337)
        : clean_snr_lin_(std::pow(10.0, clean_snr_db / 10.0)),
          jam_snr_lin_(std::pow(10.0, jam_snr_db / 10.0)),
          jammed_channels_(static_cast<int>(NUM_CHANNELS * rho)),
          gen_(seed),
          norm_dist_(0.0, 1.0),
          channel_dist_(0, NUM_CHANNELS - 1) {}

    bool transmit_symbol(bool bit) {
        int channel = channel_dist_(gen_);
        bool is_jammed = (channel < jammed_channels_);
        double snr_lin = is_jammed ? jam_snr_lin_ : clean_snr_lin_;
        double signal_amp = std::sqrt(snr_lin);

        double r0_i = (bit == false ? signal_amp : 0.0) + norm_dist_(gen_);
        double r0_q = norm_dist_(gen_);
        double energy0 = r0_i * r0_i + r0_q * r0_q;

        double r1_i = (bit == true ? signal_amp : 0.0) + norm_dist_(gen_);
        double r1_q = norm_dist_(gen_);
        double energy1 = r1_i * r1_i + r1_q * r1_q;

        return energy1 > energy0;
    }

private:
    double clean_snr_lin_;
    double jam_snr_lin_;
    int jammed_channels_;
    std::mt19937 gen_;
    std::normal_distribution<double> norm_dist_;
    std::uniform_int_distribution<int> channel_dist_;
};

// Перемішувач блокового типу на базі шаблонів C++
class BlockInterleaver {
public:
    static std::vector<bool> transform(const std::vector<bool>& input, int rows, int cols) {
        std::vector<bool> output(input.size());
        int block_size = rows * cols;
        int num_blocks = static_cast<int>(input.size()) / block_size;

        for (int b = 0; b < num_blocks; ++b) {
            int offset = b * block_size;
            for (int r = 0; r < rows; ++r) {
                for (int c = 0; c < cols; ++c) {
                    output[offset + c * rows + r] = input[offset + r * cols + c];
                }
            }
        }
        return output;
    }

    static std::vector<bool> inverse(const std::vector<bool>& input, int rows, int cols) {
        std::vector<bool> output(input.size());
        int block_size = rows * cols;
        int num_blocks = static_cast<int>(input.size()) / block_size;

        for (int b = 0; b < num_blocks; ++b) {
            int offset = b * block_size;
            for (int r = 0; r < rows; ++r) {
                for (int c = 0; c < cols; ++c) {
                    output[offset + r * cols + c] = input[offset + c * rows + r];
                }
            }
        }
        return output;
    }
};

} // namespace jamming_sim

int main() {
    using namespace jamming_sim;

    std::mt19937 gen(1337);
    std::uniform_int_distribution<int> bit_dist(0, 1);

    std::vector<bool> tx_bits(TOTAL_BITS);
    for (int i = 0; i < TOTAL_BITS; ++i) {
        tx_bits[i] = static_cast<bool>(bit_dist(gen));
    }

    FhssChannelSimulator channel(15.0, -3.0, 0.20, 1337);

    // 1. Симуляція некодованої передачі
    int uncoded_errors = 0;
    for (bool bit : tx_bits) {
        bool rx = channel.transmit_symbol(bit);
        if (rx != bit) {
            uncoded_errors++;
        }
    }

    // 2. Симуляція кодованої передачі з перемішуванням
    std::vector<bool> coded_bits;
    coded_bits.reserve(TOTAL_BITS * 3);
    for (bool bit : tx_bits) {
        coded_bits.push_back(bit);
        coded_bits.push_back(bit);
        coded_bits.push_back(bit);
    }

    auto interleaved = BlockInterleaver::transform(coded_bits, INTERLEAVER_ROWS, INTERLEAVER_COLS);

    std::vector<bool> rx_interleaved(interleaved.size());
    for (size_t i = 0; i < interleaved.size(); ++i) {
        rx_interleaved[i] = channel.transmit_symbol(interleaved[i]);
    }

    auto rx_coded = BlockInterleaver::inverse(rx_interleaved, INTERLEAVER_ROWS, INTERLEAVER_COLS);

    int coded_errors = 0;
    for (size_t i = 0; i < tx_bits.size(); ++i) {
        int votes = rx_coded[3 * i] + rx_coded[3 * i + 1] + rx_coded[3 * i + 2];
        bool decoded = (votes >= 2);
        if (decoded != tx_bits[i]) {
            coded_errors++;
        }
    }

    std::cout << std::fixed << std::setprecision(5);
    std::cout << "=== Результати симуляції частково-смугової завади (C++) ===\n";
    std::cout << "Всього бітів: " << TOTAL_BITS << ", Каналів: " << NUM_CHANNELS << "\n";
    std::cout << "BER некодованої передачі під PBJ: " << static_cast<double>(uncoded_errors) / TOTAL_BITS << "\n";
    std::cout << "BER кодованої передачі (Code+Interleaving) під PBJ: " << static_cast<double>(coded_errors) / TOTAL_BITS << "\n";

    return 0;
}
