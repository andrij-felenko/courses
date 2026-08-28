#include <cstdint>
#include <cstddef>
#include <string_view>
#include <array>
#include <algorithm>
#include <span>

class TinyLfuAdmissionFilter {
public:
    static constexpr size_t Depth = 4;
    static constexpr size_t WidthBits = 14;
    static constexpr size_t Width = 1ULL << WidthBits;
    static constexpr size_t WidthMask = Width - 1;
    static constexpr size_t SampleWindow = Width * 10;

    TinyLfuAdmissionFilter() noexcept {
        reset();
    }

    void reset() noexcept {
        for (auto& row : table_) {
            row.fill(0);
        }
        total_additions_ = 0;
    }

    // Реєстрація нового звернення до ключа
    void record_access(std::string_view key) noexcept {
        for (size_t r = 0; r < Depth; ++r) {
            const uint32_t col = static_cast<uint32_t>(hash(key, seeds_[r]) & WidthMask);
            increment_counter(r, col);
        }

        if (++total_additions_ >= SampleWindow) {
            decay();
        }
    }

    // Оцінка частоти звернень до ключа (діапазон 0..15)
    [[nodiscard]] uint8_t estimate_frequency(std::string_view key) const noexcept {
        uint8_t min_freq = 15;
        for (size_t r = 0; r < Depth; ++r) {
            const uint32_t col = static_cast<uint32_t>(hash(key, seeds_[r]) & WidthMask);
            min_freq = std::min(min_freq, get_counter(r, col));
        }
        return min_freq;
    }

    // Рішення контролера допуску: чи має кандидат витіснити поточну жертву
    [[nodiscard]] bool should_admit(std::string_view candidate_key,
                                    std::string_view victim_key) const noexcept {
        const uint8_t cand_freq = estimate_frequency(candidate_key);
        const uint8_t victim_freq = estimate_frequency(victim_key);
        return cand_freq > victim_freq;
    }

private:
    static constexpr std::array<uint64_t, Depth> seeds_ = {
        0x100000001b3ULL, 0xcbf29ce484222325ULL,
        0x811c9dc5ULL,    0x9e3779b97f4a7c15ULL
    };

    // 2 комірки по 4 біти на кожен байт
    std::array<std::array<uint8_t, Width / 2>, Depth> table_{};
    size_t total_additions_{0};

    static uint64_t hash(std::string_view key, uint64_t seed) noexcept {
        uint64_t h = seed ^ (key.size() * 0x517cc1b727220a95ULL);
        for (const unsigned char c : key) {
            h ^= static_cast<uint64_t>(c);
            h *= 0x5bd1e9955bd1e995ULL;
            h ^= h >> 47;
        }
        return h;
    }

    [[nodiscard]] uint8_t get_counter(size_t row, uint32_t col) const noexcept {
        const uint8_t byte_val = table_[row][col / 2];
        return (col & 1) ? ((byte_val >> 4) & 0x0F) : (byte_val & 0x0F);
    }

    void increment_counter(size_t row, uint32_t col) noexcept {
        const size_t byte_idx = col / 2;
        const uint8_t byte_val = table_[row][byte_idx];
        if (col & 1) {
            const uint8_t high = (byte_val >> 4) & 0x0F;
            if (high < 15) {
                table_[row][byte_idx] = (byte_val & 0x0F) | static_cast<uint8_t>((high + 1) << 4);
            }
        } else {
            const uint8_t low = byte_val & 0x0F;
            if (low < 15) {
                table_[row][byte_idx] = (byte_val & 0xF0) | static_cast<uint8_t>(low + 1);
            }
        }
    }

    void decay() noexcept {
        for (auto& row : table_) {
            for (uint8_t& b : row) {
                const uint8_t low = (b & 0x0F) >> 1;
                const uint8_t high = ((b >> 4) & 0x0F) >> 1;
                b = static_cast<uint8_t>((high << 4) | low);
            }
        }
        total_additions_ /= 2;
    }
};
