// ============================================================================
// Вбудована криптографічна система випадковості (C++20 / Embedded Modern)
// Типобезпечна, без динамічної пам'яті, RAII, std::span, constexpr
// ============================================================================

#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <bit>
#include <algorithm>
#include <expected>

namespace embedded::crypto {

// ── 1. Онлайн-тест працездатності (NIST SP 800-90B RCT) ─────────────────────
class EntropyHealthMonitor {
public:
    explicit constexpr EntropyHealthMonitor(uint32_t cutoff = 24) noexcept
        : rct_cutoff_{cutoff} {}

    enum class Error {
        SourceStuckAtConstant,
        DegradedEntropy
    };

    [[nodiscard]] constexpr std::expected<void, Error> update(uint8_t sample) noexcept {
        if (fault_) return std::unexpected(Error::SourceStuckAtConstant);

        if (sample == last_sample_) {
            repeat_count_++;
            if (repeat_count_ >= rct_cutoff_) {
                fault_ = true;
                return std::unexpected(Error::SourceStuckAtConstant);
            }
        } else {
            last_sample_ = sample;
            repeat_count_ = 1;
        }

        ones_count_ += static_cast<uint32_t>(std::popcount(sample));
        total_samples_++;
        return {};
    }

    [[nodiscard]] constexpr bool is_healthy() const noexcept { return !fault_; }
    constexpr void reset() noexcept {
        last_sample_ = 0xFF;
        repeat_count_ = 0;
        fault_ = false;
        total_samples_ = 0;
        ones_count_ = 0;
    }

private:
    uint8_t  last_sample_{0xFF};
    uint32_t repeat_count_{0};
    uint32_t rct_cutoff_{24};
    uint32_t total_samples_{0};
    uint32_t ones_count_{0};
    bool     fault_{false};
};

// ── 2. Декорелятор Джона фон Неймана ─────────────────────────────────────────
class VonNeumannExtractor {
public:
    constexpr VonNeumannExtractor() noexcept = default;

    // Приймає один сирий біт. Якщо накопичено повний байт — повертає його.
    constexpr std::expected<uint8_t, void> feed_bit(uint8_t in_bit) noexcept {
        bit_buffer_ = (bit_buffer_ << 1) | (in_bit & 1);
        bit_count_++;

        if (bit_count_ >= 2) {
            const uint8_t pair = bit_buffer_ & 0x03;
            bit_count_ = 0;

            if (pair == 0b01) {        // Пара 01 -> біт 0
                out_byte_ = (out_byte_ << 1);
                out_bits_collected_++;
            } else if (pair == 0b10) { // Пара 10 -> біт 1
                out_byte_ = (out_byte_ << 1) | 1;
                out_bits_collected_++;
            }

            if (out_bits_collected_ >= 8) {
                const uint8_t ready_byte = out_byte_;
                out_byte_ = 0;
                out_bits_collected_ = 0;
                return ready_byte;
            }
        }
        return std::unexpected();
    }

private:
    uint8_t bit_buffer_{0};
    uint8_t bit_count_{0};
    uint8_t out_byte_{0};
    uint8_t out_bits_collected_{0};
};

// ── 3. Криптографічний генератор ChaCha20-DRBG ──────────────────────────────
class ChaCha20CSPRNG {
public:
    static constexpr size_t KeySize = 32;
    static constexpr size_t BlockSize = 64;

    explicit constexpr ChaCha20CSPRNG(std::span<const uint8_t, KeySize> seed) noexcept {
        reseed(seed);
    }

    constexpr void reseed(std::span<const uint8_t, KeySize> seed) noexcept {
        // Константи ChaCha20 ("expand 32-byte k")
        state_[0] = 0x61707865;
        state_[1] = 0x3320646e;
        state_[2] = 0x79622d32;
        state_[3] = 0x6b206574;

        for (size_t i = 0; i < 8; ++i) {
            state_[4 + i] = static_cast<uint32_t>(seed[i * 4 + 0])       |
                           (static_cast<uint32_t>(seed[i * 4 + 1]) <<  8) |
                           (static_cast<uint32_t>(seed[i * 4 + 2]) << 16) |
                           (static_cast<uint32_t>(seed[i * 4 + 3]) << 24);
        }

        state_[12] = 0;
        state_[13] = 0x55AA55AA;
        state_[14] = 0x12345678;
        state_[15] = 0x9ABCDEF0;

        keystream_idx_ = BlockSize;
    }

    void generate(std::span<uint8_t> output) noexcept {
        size_t offset = 0;
        while (offset < output.size()) {
            if (keystream_idx_ >= BlockSize) {
                generate_block(state_, keystream_);
                state_[12]++;
                if (state_[12] == 0) state_[13]++;
                keystream_idx_ = 0;
            }

            const size_t available = BlockSize - keystream_idx_;
            const size_t chunk = std::min(output.size() - offset, available);

            std::copy_n(keystream_.begin() + keystream_idx_, chunk, output.begin() + offset);
            offset += chunk;
            keystream_idx_ += chunk;
        }

        // Backtracking Resistance: оновлюємо ключ новим блоком
        std::array<uint8_t, BlockSize> next_key_block{};
        generate_block(state_, next_key_block);
        state_[12]++;

        for (size_t i = 0; i < 8; ++i) {
            state_[4 + i] = static_cast<uint32_t>(next_key_block[i * 4 + 0])       |
                           (static_cast<uint32_t>(next_key_block[i * 4 + 1]) <<  8) |
                           (static_cast<uint32_t>(next_key_block[i * 4 + 2]) << 16) |
                           (static_cast<uint32_t>(next_key_block[i * 4 + 3]) << 24);
        }
        std::fill(next_key_block.begin(), next_key_block.end(), 0);
        keystream_idx_ = BlockSize;
    }

    // Заборона копіювання для запобігання дублюванню внутрішнього стану
    ChaCha20CSPRNG(const ChaCha20CSPRNG&) = delete;
    ChaCha20CSPRNG& operator=(const ChaCha20CSPRNG&) = delete;
    ChaCha20CSPRNG(ChaCha20CSPRNG&&) noexcept = default;
    ChaCha20CSPRNG& operator=(ChaCha20CSPRNG&&) noexcept = default;

private:
    static constexpr void quarter_round(uint32_t& a, uint32_t& b, uint32_t& c, uint32_t& d) noexcept {
        a += b; d ^= a; d = std::rotl(d, 16);
        c += d; b ^= c; b = std::rotl(b, 12);
        a += b; d ^= a; d = std::rotl(d,  8);
        c += d; b ^= c; b = std::rotl(b,  7);
    }

    static void generate_block(const std::array<uint32_t, 16>& in, std::array<uint8_t, 64>& out) noexcept {
        std::array<uint32_t, 16> x = in;
        for (int i = 0; i < 10; ++i) {
            quarter_round(x[0], x[4], x[ 8], x[12]);
            quarter_round(x[1], x[5], x[ 9], x[13]);
            quarter_round(x[2], x[6], x[10], x[14]);
            quarter_round(x[3], x[7], x[11], x[15]);
            quarter_round(x[0], x[5], x[10], x[15]);
            quarter_round(x[1], x[6], x[11], x[12]);
            quarter_round(x[2], x[7], x[ 8], x[13]);
            quarter_round(x[3], x[4], x[ 9], x[14]);
        }
        for (size_t i = 0; i < 16; ++i) {
            const uint32_t val = x[i] + in[i];
            out[i * 4 + 0] = static_cast<uint8_t>(val);
            out[i * 4 + 1] = static_cast<uint8_t>(val >> 8);
            out[i * 4 + 2] = static_cast<uint8_t>(val >> 16);
            out[i * 4 + 3] = static_cast<uint8_t>(val >> 24);
        }
    }

    std::array<uint32_t, 16> state_{};
    std::array<uint8_t, 64>  keystream_{};
    size_t keystream_idx_{BlockSize};
};

} // namespace embedded::crypto
