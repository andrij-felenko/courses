#include <array>
#include <span>
#include <cstdint>
#include <cstring>

void aes128_ecb_encrypt(std::span<const uint8_t, 16> key,
                        std::span<const uint8_t, 16> input,
                        std::span<uint8_t, 16> output);

namespace ble::crypto {

using Block128 = std::array<uint8_t, 16>;

inline void shift_left_128(const Block128& input, Block128& output) noexcept {
    uint8_t overflow = 0;
    for (int i = 15; i >= 0; --i) {
        uint8_t next_overflow = (input[i] & 0x80) ? 1 : 0;
        output[i] = static_cast<uint8_t>((input[i] << 1) | overflow);
        overflow = next_overflow;
    }
}

inline void generate_subkeys(const Block128& key, Block128& k1, Block128& k2) noexcept {
    constexpr Block128 zero{};
    Block128 l{};
    aes128_ecb_encrypt(key, zero, l);

    shift_left_128(l, k1);
    if (l[0] & 0x80) {
        k1[15] ^= 0x87;
    }

    shift_left_128(k1, k2);
    if (k1[0] & 0x80) {
        k2[15] ^= 0x87;
    }
}

/**
 * @brief Стандартизоване обчислення AES-CMAC
 */
void aes_cmac(std::span<const uint8_t, 16> key,
              std::span<const uint8_t> msg,
              std::span<uint8_t, 16> mac_out) noexcept {
    Block128 key_arr{};
    std::memcpy(key_arr.data(), key.data(), 16);

    Block128 k1{};
    Block128 k2{};
    generate_subkeys(key_arr, k1, k2);

    const size_t msg_len = msg.size();
    size_t n = (msg_len + 15) / 16;
    bool is_complete = false;

    if (n == 0) {
        n = 1;
        is_complete = false;
    } else {
        is_complete = (msg_len % 16 == 0);
    }

    Block128 m_last{};
    if (is_complete) {
        for (size_t i = 0; i < 16; ++i) {
            m_last[i] = msg[(n - 1) * 16 + i] ^ k1[i];
        }
    } else {
        const size_t rem = msg_len % 16;
        for (size_t i = 0; i < rem; ++i) {
            m_last[i] = msg[(n - 1) * 16 + i];
        }
        m_last[rem] = 0x80;
        for (size_t i = 0; i < 16; ++i) {
            m_last[i] ^= k2[i];
        }
    }

    Block128 x{};
    Block128 y{};

    for (size_t i = 0; i < n - 1; ++i) {
        for (size_t j = 0; j < 16; ++j) {
            y[j] = x[j] ^ msg[i * 16 + j];
        }
        aes128_ecb_encrypt(key, y, x);
    }

    for (size_t j = 0; j < 16; ++j) {
        y[j] = x[j] ^ m_last[j];
    }
    aes128_ecb_encrypt(key, y, mac_out);
}

} // namespace ble::crypto
