#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <vector>
#include <algorithm>

namespace crypto {

[[nodiscard]] constexpr uint32_t rotr(uint32_t x, uint32_t n) noexcept {
    return (x >> n) | (x << (32 - n));
}

[[nodiscard]] constexpr uint32_t ch(uint32_t x, uint32_t y, uint32_t z) noexcept {
    return (x & y) ^ (~x & z);
}

[[nodiscard]] constexpr uint32_t maj(uint32_t x, uint32_t y, uint32_t z) noexcept {
    return (x & y) ^ (x & z) ^ (y & z);
}

[[nodiscard]] constexpr uint32_t ep0(uint32_t x) noexcept {
    return rotr(x, 2) ^ rotr(x, 13) ^ rotr(x, 22);
}

[[nodiscard]] constexpr uint32_t ep1(uint32_t x) noexcept {
    return rotr(x, 6) ^ rotr(x, 11) ^ rotr(x, 25);
}

[[nodiscard]] constexpr uint32_t sig0(uint32_t x) noexcept {
    return rotr(x, 7) ^ rotr(x, 18) ^ (x >> 3);
}

[[nodiscard]] constexpr uint32_t sig1(uint32_t x) noexcept {
    return rotr(x, 17) ^ rotr(x, 19) ^ (x >> 10);
}

constexpr std::array<uint32_t, 64> K = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
};

void sha256_transform_block(std::array<uint32_t, 8>& state,
                            std::span<const uint8_t, 64> block) noexcept {
    std::array<uint32_t, 64> w{};
    for (size_t i = 0; i < 16; ++i) {
        w[i] = (static_cast<uint32_t>(block[i * 4]) << 24) |
               (static_cast<uint32_t>(block[i * 4 + 1]) << 16) |
               (static_cast<uint32_t>(block[i * 4 + 2]) << 8) |
               (static_cast<uint32_t>(block[i * 4 + 3]));
    }
    for (size_t i = 16; i < 64; ++i) {
        w[i] = sig1(w[i - 2]) + w[i - 7] + sig0(w[i - 15]) + w[i - 16];
    }

    uint32_t a = state[0], b = state[1], c = state[2], d = state[3];
    uint32_t e = state[4], f = state[5], g = state[6], h = state[7];

    for (size_t i = 0; i < 64; ++i) {
        const uint32_t t1 = h + ep1(e) + ch(e, f, g) + K[i] + w[i];
        const uint32_t t2 = ep0(a) + maj(a, b, c);
        h = g; g = f; f = e; e = d + t1;
        d = c; c = b; b = a; a = t1 + t2;
    }

    state[0] += a; state[1] += b; state[2] += c; state[3] += d;
    state[4] += e; state[5] += f; state[6] += g; state[7] += h;
}

[[nodiscard]] std::vector<uint8_t> build_md_padding(size_t total_len_bytes) {
    std::vector<uint8_t> pad;
    pad.push_back(0x80);

    size_t current_len = total_len_bytes + 1;
    while ((current_len % 64) != 56) {
        pad.push_back(0x00);
        current_len++;
    }

    const uint64_t bit_len = static_cast<uint64_t>(total_len_bytes) * 8;
    for (int i = 7; i >= 0; --i) {
        pad.push_back(static_cast<uint8_t>((bit_len >> (i * 8)) & 0xFF));
    }
    return pad;
}

struct ForgeryResult {
    std::vector<uint8_t> forged_message;
    std::array<uint32_t, 8> forged_hash;
};

[[nodiscard]] ForgeryResult length_extension_attack(
    const std::array<uint32_t, 8>& original_hash,
    size_t key_len,
    std::span<const uint8_t> orig_msg,
    std::span<const uint8_t> extension) {

    const size_t total_orig_bytes = key_len + orig_msg.size();
    const std::vector<uint8_t> pad = build_md_padding(total_orig_bytes);

    std::vector<uint8_t> forged_msg;
    forged_msg.reserve(orig_msg.size() + pad.size() + extension.size());
    forged_msg.insert(forged_msg.end(), orig_msg.begin(), orig_msg.end());
    forged_msg.insert(forged_msg.end(), pad.begin(), pad.end());
    forged_msg.insert(forged_msg.end(), extension.begin(), extension.end());

    std::array<uint32_t, 8> forged_state = original_hash;

    const size_t new_total_bytes = total_orig_bytes + pad.size() + extension.size();
    const std::vector<uint8_t> ext_pad = build_md_padding(new_total_bytes);

    std::vector<uint8_t> ext_stream;
    ext_stream.reserve(extension.size() + ext_pad.size());
    ext_stream.insert(ext_stream.end(), extension.begin(), extension.end());
    ext_stream.insert(ext_stream.end(), ext_pad.begin(), ext_pad.end());

    for (size_t offset = 0; offset < ext_stream.size(); offset += 64) {
        std::span<const uint8_t, 64> block(ext_stream.data() + offset, 64);
        sha256_transform_block(forged_state, block);
    }

    return {std::move(forged_msg), forged_state};
}

} // namespace crypto
