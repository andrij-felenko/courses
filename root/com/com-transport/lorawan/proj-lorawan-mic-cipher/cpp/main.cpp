#include <array>
#include <span>
#include <cstdint>
#include <cstring>
#include <algorithm>

namespace lorawan::crypto {

// Таблиця підстановок S-Box алгоритму AES
inline constexpr std::array<uint8_t, 256> sbox = {
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
};

constexpr uint8_t xtime(uint8_t x) noexcept {
    return static_cast<uint8_t>((x << 1) ^ (((x >> 7) & 1) * 0x1b));
}

// Криптографічний рушій AES-128
class Aes128Engine {
public:
    explicit Aes128Engine(std::span<const uint8_t, 16> key) noexcept {
        expand_key(key);
    }

    void encrypt_block(std::span<const uint8_t, 16> in, std::span<uint8_t, 16> out) const noexcept {
        std::array<uint8_t, 16> state{};
        for (size_t i = 0; i < 16; ++i) state[i] = in[i] ^ round_keys_[i];

        for (int round = 1; round <= 10; ++round) {
            for (size_t i = 0; i < 16; ++i) state[i] = sbox[state[i]];

            // ShiftRows
            uint8_t t = state[1]; state[1] = state[5]; state[5] = state[9]; state[9] = state[13]; state[13] = t;
            t = state[2]; state[2] = state[10]; state[10] = t; t = state[6]; state[6] = state[14]; state[14] = t;
            t = state[15]; state[15] = state[11]; state[11] = state[7]; state[7] = state[3]; state[3] = t;

            if (round < 10) {
                // MixColumns
                for (size_t i = 0; i < 4; ++i) {
                    size_t c = i * 4;
                    uint8_t a = state[c], b = state[c + 1], c_val = state[c + 2], d = state[c + 3];
                    state[c]     = xtime(a ^ b) ^ b ^ c_val ^ d;
                    state[c + 1] = xtime(b ^ c_val) ^ c_val ^ d ^ a;
                    state[c + 2] = xtime(c_val ^ d) ^ d ^ a ^ b;
                    state[c + 3] = xtime(d ^ a) ^ a ^ b ^ c_val;
                }
            }
            for (size_t i = 0; i < 16; ++i) state[i] ^= round_keys_[round * 16 + i];
        }
        std::copy(state.begin(), state.end(), out.begin());
    }

private:
    std::array<uint8_t, 176> round_keys_{};

    void expand_key(std::span<const uint8_t, 16> key) noexcept {
        constexpr std::array<uint8_t, 10> rcon = {0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36};
        std::copy(key.begin(), key.end(), round_keys_.begin());
        for (size_t i = 4; i < 44; ++i) {
            std::array<uint8_t, 4> temp{};
            std::copy_n(&round_keys_[(i - 1) * 4], 4, temp.begin());
            if (i % 4 == 0) {
                uint8_t k = temp[0];
                temp[0] = sbox[temp[1]] ^ rcon[(i / 4) - 1];
                temp[1] = sbox[temp[2]];
                temp[2] = sbox[temp[3]];
                temp[3] = sbox[k];
            }
            for (size_t j = 0; j < 4; ++j) {
                round_keys_[i * 4 + j] = round_keys_[(i - 4) * 4 + j] ^ temp[j];
            }
        }
    }
};

void cmac_shift_left(std::span<const uint8_t, 16> in, std::span<uint8_t, 16> out) noexcept {
    uint8_t overflow = 0;
    for (int i = 15; i >= 0; --i) {
        out[i] = static_cast<uint8_t>((in[i] << 1) | overflow);
        overflow = (in[i] & 0x80) ? 1 : 0;
    }
    if (in[0] & 0x80) {
        out[15] ^= 0x87;
    }
}

// Розрахунок коду цілісності MIC з гарантією відсутності динамічної пам'яті
[[nodiscard]] uint32_t compute_mic(std::span<const uint8_t> msg,
                                   uint32_t dev_addr, uint32_t fcnt,
                                   uint8_t dir, std::span<const uint8_t, 16> nwk_skey) noexcept {
    const Aes128Engine aes(nwk_skey);

    std::array<uint8_t, 16> zero{};
    std::array<uint8_t, 16> l{}, k1{}, k2{};
    aes.encrypt_block(zero, l);
    cmac_shift_left(l, k1);
    cmac_shift_left(k1, k2);

    std::array<uint8_t, 16> b0{};
    b0[0] = 0x49;
    b0[5] = dir;
    b0[6] = static_cast<uint8_t>(dev_addr & 0xFF);
    b0[7] = static_cast<uint8_t>((dev_addr >> 8) & 0xFF);
    b0[8] = static_cast<uint8_t>((dev_addr >> 16) & 0xFF);
    b0[9] = static_cast<uint8_t>((dev_addr >> 24) & 0xFF);
    b0[10] = static_cast<uint8_t>(fcnt & 0xFF);
    b0[11] = static_cast<uint8_t>((fcnt >> 8) & 0xFF);
    b0[12] = static_cast<uint8_t>((fcnt >> 16) & 0xFF);
    b0[13] = static_cast<uint8_t>((fcnt >> 24) & 0xFF);
    b0[15] = static_cast<uint8_t>(msg.size());

    const size_t total_len = 16 + msg.size();
    const size_t n_blocks = (total_len + 15) / 16;
    const bool is_last_complete = (total_len % 16 == 0);

    std::array<uint8_t, 16> x{}, y{};

    for (size_t i = 0; i < n_blocks; ++i) {
        std::array<uint8_t, 16> block{};
        const size_t block_offset = i * 16;

        for (size_t j = 0; j < 16; ++j) {
            size_t idx = block_offset + j;
            if (idx < 16) {
                block[j] = b0[idx];
            } else if (idx < total_len) {
                block[j] = msg[idx - 16];
            } else if (idx == total_len) {
                block[j] = 0x80;
            }
        }

        if (i == n_blocks - 1) {
            const auto& k = is_last_complete ? k1 : k2;
            for (size_t j = 0; j < 16; ++j) block[j] ^= k[j];
        }

        for (size_t j = 0; j < 16; ++j) y[j] = x[j] ^ block[j];
        aes.encrypt_block(y, x);
    }

    return static_cast<uint32_t>(x[0]) |
          (static_cast<uint32_t>(x[1]) << 8) |
          (static_cast<uint32_t>(x[2]) << 16) |
          (static_cast<uint32_t>(x[3]) << 24);
}

// Потокове шифрування корисного навантаження (AES-128 CTR)
void cipher_payload(std::span<uint8_t> payload,
                    uint32_t dev_addr, uint32_t fcnt,
                    uint8_t dir, std::span<const uint8_t, 16> key) noexcept {
    if (payload.empty()) return;

    const Aes128Engine aes(key);

    std::array<uint8_t, 16> a_block{};
    a_block[0] = 0x01;
    a_block[5] = dir;
    a_block[6] = static_cast<uint8_t>(dev_addr & 0xFF);
    a_block[7] = static_cast<uint8_t>((dev_addr >> 8) & 0xFF);
    a_block[8] = static_cast<uint8_t>((dev_addr >> 16) & 0xFF);
    a_block[9] = static_cast<uint8_t>((dev_addr >> 24) & 0xFF);
    a_block[10] = static_cast<uint8_t>(fcnt & 0xFF);
    a_block[11] = static_cast<uint8_t>((fcnt >> 8) & 0xFF);
    a_block[12] = static_cast<uint8_t>((fcnt >> 16) & 0xFF);
    a_block[13] = static_cast<uint8_t>((fcnt >> 24) & 0xFF);

    const size_t n_blocks = (payload.size() + 15) / 16;
    for (size_t i = 1; i <= n_blocks; ++i) {
        a_block[15] = static_cast<uint8_t>(i);
        std::array<uint8_t, 16> s_block{};
        aes.encrypt_block(a_block, s_block);

        const size_t bytes_to_xor = (i == n_blocks && payload.size() % 16 != 0) ? (payload.size() % 16) : 16;
        for (size_t j = 0; j < bytes_to_xor; ++j) {
            payload[(i - 1) * 16 + j] ^= s_block[j];
        }
    }
}

} // namespace lorawan::crypto
