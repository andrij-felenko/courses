#include <cstdint>
#include <cstddef>
#include <cstring>
#include <span>
#include <array>
#include <string_view>
#include <bit>

class Sha256Extension {
public:
    using Digest = std::array<uint8_t, 32>;

    /* Ініціалізація стану захопленим гешем */
    explicit Sha256Extension(std::span<const uint8_t, 32> original_hash, uint64_t total_previous_bytes) noexcept
        : bit_count_{total_previous_bytes * 8} {
        for (size_t i = 0; i < 8; ++i) {
            state_[i] = (static_cast<uint32_t>(original_hash[i * 4]) << 24) |
                        (static_cast<uint32_t>(original_hash[i * 4 + 1]) << 16) |
                        (static_cast<uint32_t>(original_hash[i * 4 + 2]) << 8) |
                        (static_cast<uint32_t>(original_hash[i * 4 + 3]));
        }
        buffer_.fill(0);
    }

    void update(std::span<const uint8_t> data) noexcept {
        size_t buffer_fill = static_cast<size_t>((bit_count_ / 8) % 64);
        bit_count_ += data.size() * 8;

        size_t offset = 0;
        while (offset < data.size()) {
            size_t to_copy = std::min(64 - buffer_fill, data.size() - offset);
            std::memcpy(buffer_.data() + buffer_fill, data.data() + offset, to_copy);
            buffer_fill += to_copy;
            offset += to_copy;

            if (buffer_fill == 64) {
                transform(buffer_.data());
                buffer_fill = 0;
            }
        }
    }

    [[nodiscard]] Digest finalize() noexcept {
        size_t buffer_fill = static_cast<size_t>((bit_count_ / 8) % 64);
        buffer_[buffer_fill++] = 0x80;

        if (buffer_fill > 56) {
            std::fill(buffer_.begin() + buffer_fill, buffer_.end(), uint8_t{0});
            transform(buffer_.data());
            buffer_fill = 0;
        }
        std::fill(buffer_.begin() + buffer_fill, buffer_.begin() + 56, uint8_t{0});

        for (size_t i = 0; i < 8; ++i) {
            buffer_[63 - i] = static_cast<uint8_t>(bit_count_ >> (i * 8));
        }
        transform(buffer_.data());

        Digest out{};
        for (size_t i = 0; i < 8; ++i) {
            out[i * 4]     = static_cast<uint8_t>(state_[i] >> 24);
            out[i * 4 + 1] = static_cast<uint8_t>(state_[i] >> 16);
            out[i * 4 + 2] = static_cast<uint8_t>(state_[i] >> 8);
            out[i * 4 + 3] = static_cast<uint8_t>(state_[i]);
        }
        return out;
    }

private:
    static constexpr std::array<uint32_t, 64> K = {
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
        0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
        0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
        0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
        0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
        0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
        0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
        0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
        0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    };

    void transform(const uint8_t* block) noexcept {
        std::array<uint32_t, 64> w{};
        for (size_t i = 0; i < 16; ++i) {
            w[i] = (static_cast<uint32_t>(block[i * 4]) << 24) |
                   (static_cast<uint32_t>(block[i * 4 + 1]) << 16) |
                   (static_cast<uint32_t>(block[i * 4 + 2]) << 8) |
                   (static_cast<uint32_t>(block[i * 4 + 3]));
        }
        for (size_t i = 16; i < 64; ++i) {
            uint32_t s0 = std::rotr(w[i - 15], 7) ^ std::rotr(w[i - 15], 18) ^ (w[i - 15] >> 3);
            uint32_t s1 = std::rotr(w[i - 2], 17) ^ std::rotr(w[i - 2], 19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16] + s0 + w[i - 7] + s1;
        }

        uint32_t a = state_[0], b = state_[1], c = state_[2], d = state_[3];
        uint32_t e = state_[4], f = state_[5], g = state_[6], h = state_[7];

        for (size_t i = 0; i < 64; ++i) {
            uint32_t s1 = std::rotr(e, 6) ^ std::rotr(e, 11) ^ std::rotr(e, 25);
            uint32_t ch = (e & f) ^ ((~e) & g);
            uint32_t temp1 = h + s1 + ch + K[i] + w[i];
            uint32_t s0 = std::rotr(a, 2) ^ std::rotr(a, 13) ^ std::rotr(a, 22);
            uint32_t maj = (a & b) ^ (a & c) ^ (b & c);
            uint32_t temp2 = s0 + maj;

            h = g; g = f; f = e; e = d + temp1;
            d = c; c = b; b = a; a = temp1 + temp2;
        }

        state_[0] += a; state_[1] += b; state_[2] += c; state_[3] += d;
        state_[4] += e; state_[5] += f; state_[6] += g; state_[7] += h;
    }

    std::array<uint32_t, 8> state_{};
    uint64_t bit_count_{0};
    std::array<uint8_t, 64> buffer_{};
};
