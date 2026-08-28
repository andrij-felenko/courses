#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <memory>
#include <span>
#include <optional>
#include <algorithm>
#include <iomanip>

namespace communications {

enum class ChannelState {
    Good = 0,
    Bad = 1
};

struct ChannelConfig {
    double p_gb{0.01};   // Ймовірність G -> B
    double p_bg{0.10};   // Ймовірність B -> G
    double e_g{0.0001};  // Помилка в стані G
    double e_b{0.50};    // Помилка в стані B
    double snr_db{8.0};  // Співвідношення сигнал/шум
};

struct TransmissionStats {
    uint64_t total_bits{0};
    uint64_t total_errors{0};
    uint64_t bad_state_bits{0};
    uint64_t burst_count{0};
    uint64_t current_burst_len{0};
    uint64_t max_burst_len{0};
};

// Ідіоматичний клас марковського каналу Гілберта-Елліота
class GilbertElliottChannel {
public:
    explicit GilbertElliottChannel(const ChannelConfig& config, uint32_t seed = 42)
        : config_(config), rng_(seed), dist_uniform_(0.0, 1.0), dist_gauss_(0.0, 1.0) {
        snr_linear_ = std::pow(10.0, config_.snr_db / 10.0);
    }

    struct TransmitResult {
        bool bit;
        double llr;
        bool was_error;
    };

    TransmitResult transmit_bit(bool tx_bit) {
        stats_.total_bits++;

        // Оновлення стану дискретного марковського ланцюга
        if (current_state_ == ChannelState::Good) {
            if (dist_uniform_(rng_) < config_.p_gb) {
                current_state_ = ChannelState::Bad;
                stats_.burst_count++;
                stats_.current_burst_len = 1;
            }
        } else {
            stats_.bad_state_bits++;
            stats_.current_burst_len++;
            stats_.max_burst_len = std::max(stats_.max_burst_len, stats_.current_burst_len);
            if (dist_uniform_(rng_) < config_.p_bg) {
                current_state_ = ChannelState::Good;
                stats_.current_burst_len = 0;
            }
        }

        // Ймовірність помилки залежно від поточного стану
        double err_prob = (current_state_ == ChannelState::Good) ? config_.e_g : config_.e_b;
        bool is_error = (dist_uniform_(rng_) < err_prob);
        bool rx_bit = tx_bit ^ is_error;

        if (is_error) {
            stats_.total_errors++;
        }

        // BPSK та гауссів шум для обчислення LLR
        double noise_sigma = (current_state_ == ChannelState::Good) 
                             ? 1.0 / std::sqrt(2.0 * snr_linear_)
                             : 2.5 / std::sqrt(2.0 * snr_linear_);
        double s = tx_bit ? 1.0 : -1.0;
        double y = s + dist_gauss_(rng_) * noise_sigma;
        double rx_llr = 2.0 * y / (noise_sigma * noise_sigma);

        return {rx_bit, rx_llr, is_error};
    }

    [[nodiscard]] const TransmissionStats& stats() const noexcept { return stats_; }
    void reset_stats() noexcept {
        stats_ = TransmissionStats{};
        current_state_ = ChannelState::Good;
    }

private:
    ChannelConfig config_;
    double snr_linear_;
    ChannelState current_state_{ChannelState::Good};
    TransmissionStats stats_{};
    std::mt19937 rng_;
    std::uniform_real_distribution<double> dist_uniform_;
    std::normal_distribution<double> dist_gauss_;
};

// Блоковий матричний переміжник
class BlockInterleaver {
public:
    BlockInterleaver(size_t rows, size_t cols)
        : rows_(rows), cols_(cols), matrix_(rows * cols, false) {}

    [[nodiscard]] std::vector<bool> interleave(std::span<const bool> input) {
        std::copy(input.begin(), input.end(), matrix_.begin());
        std::vector<bool> output(rows_ * cols_);
        size_t out_idx = 0;
        for (size_t c = 0; c < cols_; ++c) {
            for (size_t r = 0; r < rows_; ++r) {
                output[out_idx++] = matrix_[r * cols_ + c];
            }
        }
        return output;
    }

    [[nodiscard]] std::vector<bool> deinterleave(std::span<const bool> input) {
        size_t in_idx = 0;
        for (size_t c = 0; c < cols_; ++c) {
            for (size_t r = 0; r < rows_; ++r) {
                matrix_[r * cols_ + c] = input[in_idx++];
            }
        }
        std::vector<bool> output(rows_ * cols_);
        std::copy(matrix_.begin(), matrix_.end(), output.begin());
        return output;
    }

private:
    size_t rows_;
    size_t cols_;
    std::vector<bool> matrix_;
};

// Кодер і декодер Хеммінга (7, 4)
class HammingCode74 {
public:
    static constexpr size_t kDataBits = 4;
    static constexpr size_t kCodeBits = 7;

    static std::vector<bool> encode(std::span<const bool, kDataBits> d) {
        return {
            d[0], d[1], d[2], d[3],
            static_cast<bool>(d[0] ^ d[1] ^ d[2]),
            static_cast<bool>(d[1] ^ d[2] ^ d[3]),
            static_cast<bool>(d[0] ^ d[2] ^ d[3])
        };
    }

    static std::optional<std::vector<bool>> decode(std::span<const bool, kCodeBits> r) {
        bool s0 = r[0] ^ r[1] ^ r[2] ^ r[4];
        bool s1 = r[1] ^ r[2] ^ r[3] ^ r[5];
        bool s2 = r[0] ^ r[2] ^ r[3] ^ r[6];
        int syndrome = (static_cast<int>(s2) << 2) | (static_cast<int>(s1) << 1) | static_cast<int>(s0);

        std::vector<bool> corr(r.begin(), r.end());
        if (syndrome == 5) corr[0] = !corr[0];
        else if (syndrome == 3) corr[1] = !corr[1];
        else if (syndrome == 7) corr[2] = !corr[2];
        else if (syndrome == 6) corr[3] = !corr[3];
        else if (syndrome == 1) corr[4] = !corr[4];
        else if (syndrome == 2) corr[5] = !corr[5];
        else if (syndrome == 4) corr[6] = !corr[6];

        bool re_s0 = corr[0] ^ corr[1] ^ corr[2] ^ corr[4];
        bool re_s1 = corr[1] ^ corr[2] ^ corr[3] ^ corr[5];
        bool re_s2 = corr[0] ^ corr[2] ^ corr[3] ^ corr[6];

        if (re_s0 || re_s1 || re_s2) {
            return std::nullopt; // Невиправна помилка
        }

        return std::vector<bool>{corr[0], corr[1], corr[2], corr[3]};
    }
};

} // namespace communications

int main() {
    using namespace communications;

    ChannelConfig cfg{.p_gb = 0.01, .p_bg = 0.10, .e_g = 0.0001, .e_b = 0.50, .snr_db = 8.0};
    GilbertElliottChannel channel(cfg, 42);

    constexpr size_t num_blocks = 10000;
    constexpr size_t int_depth = 16;

    std::mt19937 data_rng(123);
    std::uniform_int_distribution<int> bit_dist(0, 1);

    // Генерація тестових даних
    std::vector<bool> tx_data(num_blocks * HammingCode74::kDataBits);
    std::vector<bool> tx_coded(num_blocks * HammingCode74::kCodeBits);

    for (size_t i = 0; i < tx_data.size(); ++i) {
        tx_data[i] = bit_dist(data_rng);
    }

    for (size_t b = 0; b < num_blocks; ++b) {
        std::span<const bool, 4> block_span(&tx_data[b * 4], 4);
        auto coded = HammingCode74::encode(block_span);
        std::copy(coded.begin(), coded.end(), &tx_coded[b * 7]);
    }

    std::cout << "=== Симуляція каналу Гілберта-Елліота в C++20 ===\n";
    std::cout << "P_GB = " << cfg.p_gb << ", P_BG = " << cfg.p_bg 
              << ", Середня пачка = " << 1.0 / cfg.p_bg << " бітів\n\n";

    // 1. FEC без перемішування
    size_t fec_errors_no_int = 0;
    for (size_t b = 0; b < num_blocks; ++b) {
        std::array<bool, 7> rx_block{};
        for (size_t i = 0; i < 7; ++i) {
            rx_block[i] = channel.transmit_bit(tx_coded[b * 7 + i]).bit;
        }
        auto decoded = HammingCode74::decode(rx_block);
        if (!decoded || !std::equal(decoded->begin(), decoded->end(), tx_data.begin() + b * 4)) {
            fec_errors_no_int++;
        }
    }

    // 2. FEC з перемішуванням
    channel.reset_stats();
    BlockInterleaver interleaver(int_depth, HammingCode74::kCodeBits);
    size_t groups = num_blocks / int_depth;
    size_t fec_errors_with_int = 0;

    for (size_t g = 0; g < groups; ++g) {
        std::span<const bool> group_span(&tx_coded[g * int_depth * 7], int_depth * 7);
        auto interleaved = interleaver.interleave(group_span);

        std::vector<bool> rx_interleaved(interleaved.size());
        for (size_t i = 0; i < interleaved.size(); ++i) {
            rx_interleaved[i] = channel.transmit_bit(interleaved[i]).bit;
        }

        auto deinterleaved = interleaver.deinterleave(rx_interleaved);
        for (size_t b = 0; b < int_depth; ++b) {
            std::array<bool, 7> blk{};
            std::copy_n(deinterleaved.begin() + b * 7, 7, blk.begin());
            auto decoded = HammingCode74::decode(blk);
            if (!decoded || !std::equal(decoded->begin(), decoded->end(), tx_data.begin() + (g * int_depth + b) * 4)) {
                fec_errors_with_int++;
            }
        }
    }

    // 3. Chase Combining HARQ
    channel.reset_stats();
    size_t harq_success = 0;
    size_t harq_transmissions = 0;
    constexpr size_t max_retries = 4;

    for (size_t b = 0; b < num_blocks; ++b) {
        std::array<double, 7> acc_llr{};
        bool success = false;

        for (size_t attempt = 0; attempt < max_retries && !success; ++attempt) {
            harq_transmissions++;
            std::array<bool, 7> rx_hard{};
            for (size_t i = 0; i < 7; ++i) {
                auto res = channel.transmit_bit(tx_coded[b * 7 + i]);
                acc_llr[i] += res.llr;
                rx_hard[i] = (acc_llr[i] > 0.0);
            }
            auto decoded = HammingCode74::decode(rx_hard);
            if (decoded && std::equal(decoded->begin(), decoded->end(), tx_data.begin() + b * 4)) {
                success = true;
                harq_success++;
            }
        }
    }

    std::cout << std::scientific << std::setprecision(4);
    std::cout << "Результати тестування:\n";
    std::cout << "1. FEC без перемішування BLER:      " 
              << static_cast<double>(fec_errors_no_int) / num_blocks << '\n';
    std::cout << "2. FEC з перемішуванням (D=" << int_depth << ") BLER: " 
              << static_cast<double>(fec_errors_with_int) / (groups * int_depth) << '\n';
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "3. Chase Combining HARQ успішність: " 
              << (100.0 * harq_success / num_blocks) << "% (сер. спроб: "
              << (static_cast<double>(harq_transmissions) / num_blocks) << ")\n";

    return 0;
}
