#ifndef SRAM_PUF_ANALYZER_HPP
#define SRAM_PUF_ANALYZER_HPP

#include <vector>
#include <cstdint>
#include <span>
#include <bitset>
#include <iostream>
#include <numeric>
#include <algorithm>

namespace puf {

class SramPufAnalyzer {
public:
    static constexpr std::size_t BlockSize = 64;
    static constexpr std::size_t TotalBits = BlockSize * 8;

    SramPufAnalyzer() = default;

    /* Додавання вибірки відбитка з чергового циклу живлення */
    void add_sample(std::span<const std::uint8_t, BlockSize> sample) {
        std::bitset<TotalBits> sample_bits;
        for (std::size_t i = 0; i < BlockSize; ++i) {
            for (int bit = 0; bit < 8; ++bit) {
                if ((sample[i] >> bit) & 1) {
                    sample_bits.set(i * 8 + bit);
                }
            }
        }
        samples_.push_back(sample_bits);
    }

    /* Обчислення маски стабільних бітів (біти, які не змінюють значення між вибірками) */
    [[nodiscard]] std::bitset<TotalBits> generate_stable_mask() const {
        if (samples_.empty()) return {};

        std::bitset<TotalBits> stable_mask;
        stable_mask.set(); /* Спочатку припускаємо всі біти стабільними */

        for (std::size_t bit = 0; bit < TotalBits; ++bit) {
            bool first_val = samples_[0][bit];
            for (std::size_t i = 1; i < samples_.size(); ++i) {
                if (samples_[i][bit] != first_val) {
                    stable_mask.reset(bit); /* Біт хиткий (unstable) */
                    break;
                }
            }
        }
        return stable_mask;
    }

    /* Обчислення середньої відстані Геммінга відносно першої вибірки */
    [[nodiscard]] double calculate_average_intra_ber() const {
        if (samples_.size() < 2) return 0.0;

        std::size_t total_errors = 0;
        const auto& ref = samples_[0];

        for (std::size_t i = 1; i < samples_.size(); ++i) {
            total_errors += (ref ^ samples_[i]).count();
        }

        double avg_dist = static_cast<double>(total_errors) / static_cast<double>(samples_.size() - 1);
        return (avg_dist / TotalBits) * 100.0;
    }

private:
    std::vector<std::bitset<TotalBits>> samples_;
};

} // namespace puf

#endif // SRAM_PUF_ANALYZER_HPP
