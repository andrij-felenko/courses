#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <bit>

class CryptoFhssHopEngine {
public:
    static constexpr size_t kMaxChannels = 256;
    static constexpr size_t kKeySize = 16;

    CryptoFhssHopEngine() = default;

    CryptoFhssHopEngine(std::span<const uint8_t, kKeySize> key,
                        uint32_t net_id,
                        uint16_t num_channels) noexcept
        : net_id_(net_id), num_channels_(num_channels > kMaxChannels ? kMaxChannels : num_channels) {
        for (size_t i = 0; i < 4; ++i) {
            key_[i] = static_cast<uint32_t>(key[i * 4 + 0]) |
                     (static_cast<uint32_t>(key[i * 4 + 1]) << 8) |
                     (static_cast<uint32_t>(key[i * 4 + 2]) << 16) |
                     (static_cast<uint32_t>(key[i * 4 + 3]) << 24);
        }
        blacklist_mask_.fill(0);
    }

    void set_channel_blocked(uint16_t ch, bool blocked) noexcept {
        if (ch >= num_channels_) return;
        if (blocked) {
            blacklist_mask_[ch / 8] |= static_cast<uint8_t>(1u << (ch % 8));
        } else {
            blacklist_mask_[ch / 8] &= static_cast<uint8_t>(~(1u << (ch % 8)));
        }
    }

    [[nodiscard]] bool is_channel_blocked(uint16_t ch) const noexcept {
        if (ch >= num_channels_) return true;
        return (blacklist_mask_[ch / 8] & (1u << (ch % 8))) != 0;
    }

    [[nodiscard]] uint16_t get_channel(uint64_t hop_counter) const noexcept {
        if (num_channels_ == 0) return 0;

        for (uint32_t attempt = 0; attempt < 8; ++attempt) {
            const uint32_t rand_val = evaluate_prf(hop_counter, attempt);
            const uint16_t candidate = reduce_unbiased(rand_val, num_channels_);

            if (!is_channel_blocked(candidate)) {
                return candidate;
            }
        }
        return static_cast<uint16_t>(hop_counter % num_channels_);
    }

    [[nodiscard]] uint16_t channel_count() const noexcept { return num_channels_; }

private:
    std::array<uint32_t, 4> key_{};
    uint32_t net_id_{0};
    uint16_t num_channels_{0};
    std::array<uint8_t, kMaxChannels / 8> blacklist_mask_{};

    static void quarter_round(uint32_t& a, uint32_t& b, uint32_t& c, uint32_t& d) noexcept {
        a += b; d ^= a; d = std::rotl(d, 16);
        c += d; b ^= c; b = std::rotl(b, 12);
        a += b; d ^= a; d = std::rotl(d, 8);
        c += d; b ^= c; b = std::rotl(b, 7);
    }

    [[nodiscard]] uint32_t evaluate_prf(uint64_t hop_counter, uint32_t attempt) const noexcept {
        std::array<uint32_t, 4> state = {
            key_[0] ^ static_cast<uint32_t>(hop_counter & 0xFFFFFFFFu),
            key_[1] ^ static_cast<uint32_t>(hop_counter >> 32),
            key_[2] ^ net_id_,
            key_[3] ^ attempt
        };

        for (int r = 0; r < 4; ++r) {
            quarter_round(state[0], state[1], state[2], state[3]);
        }
        return state[0] ^ state[1] ^ state[2] ^ state[3];
    }

    [[nodiscard]] static constexpr uint16_t reduce_unbiased(uint32_t raw_val, uint16_t bound) noexcept {
        const auto mult = static_cast<uint64_t>(raw_val) * static_cast<uint64_t>(bound);
        return static_cast<uint16_t>(mult >> 32);
    }
};
