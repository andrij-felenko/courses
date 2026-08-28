#include <array>
#include <span>
#include <cstdint>
#include <functional>
#include <algorithm>

namespace bluetooth::crypto {

inline constexpr std::size_t aes_block_size = 16;

using Block = std::array<std::uint8_t, aes_block_size>;
using PointCoord = std::array<std::uint8_t, 32>;
using Nonce = std::array<std::uint8_t, 16>;

using AesEncryptFn = std::function<void(std::span<const std::uint8_t, 16> key,
                                       std::span<const std::uint8_t, 16> in,
                                       std::span<std::uint8_t, 16> out)>;

namespace detail {

constexpr void shift_left(std::span<const std::uint8_t, aes_block_size> in,
                         std::span<std::uint8_t, aes_block_size> out) noexcept {
    std::uint8_t overflow = 0;
    for (int i = static_cast<int>(aes_block_size) - 1; i >= 0; --i) {
        out[i] = static_cast<std::uint8_t>((in[i] << 1) | overflow);
        overflow = static_cast<std::uint8_t>((in[i] & 0x80) ? 1 : 0);
    }
}

void generate_subkeys(std::span<const std::uint8_t, 16> key,
                      Block& k1, Block& k2,
                      const AesEncryptFn& encrypt) {
    Block zero{};
    Block l{};
    encrypt(key, zero, l);

    shift_left(l, k1);
    if (l[0] & 0x80) {
        k1[15] ^= 0x87;
    }

    shift_left(k1, k2);
    if (k1[0] & 0x80) {
        k2[15] ^= 0x87;
    }
}

} // namespace detail

Block aes_cmac(std::span<const std::uint8_t, 16> key,
               std::span<const std::uint8_t> message,
               const AesEncryptFn& encrypt) {
    Block k1{}, k2{};
    detail::generate_subkeys(key, k1, k2, encrypt);

    const auto len = message.size();
    std::size_t n_blocks = (len + aes_block_size - 1) / aes_block_size;
    if (n_blocks == 0) {
        n_blocks = 1;
    }

    const bool last_complete = (len > 0) && (len % aes_block_size == 0);
    Block x{};
    Block y{};

    for (std::size_t i = 0; i < n_blocks - 1; ++i) {
        for (std::size_t b = 0; b < aes_block_size; ++b) {
            y[b] = x[b] ^ message[i * aes_block_size + b];
        }
        encrypt(key, y, x);
    }

    Block last_block{};
    const std::size_t last_len = len - (n_blocks - 1) * aes_block_size;
    if (last_complete) {
        for (std::size_t b = 0; b < aes_block_size; ++b) {
            last_block[b] = message[(n_blocks - 1) * aes_block_size + b] ^ k1[b];
        }
    } else {
        if (last_len > 0) {
            std::copy_n(message.data() + (n_blocks - 1) * aes_block_size, last_len, last_block.data());
        }
        last_block[last_len] = 0x80;
        for (std::size_t b = 0; b < aes_block_size; ++b) {
            last_block[b] ^= k2[b];
        }
    }

    for (std::size_t b = 0; b < aes_block_size; ++b) {
        y[b] = x[b] ^ last_block[b];
    }
    Block mac{};
    encrypt(key, y, mac);
    return mac;
}

/* Функція криптографічного зобов'язання f4 */
Block calculate_f4(const PointCoord& pka_x, const PointCoord& pkb_x,
                   const Nonce& nonce, std::uint8_t z_flag,
                   const AesEncryptFn& encrypt) {
    std::array<std::uint8_t, 65> msg{};
    std::copy_n(pka_x.data(), 32, msg.data());
    std::copy_n(pkb_x.data(), 32, msg.data() + 32);
    msg[64] = z_flag;

    return aes_cmac(nonce, msg, encrypt);
}

/* Розрахунок 6-значного коду Numeric Comparison g2 */
std::uint32_t calculate_g2(const PointCoord& pka_x, const PointCoord& pkb_x,
                           const Nonce& na, const Nonce& nb,
                           const AesEncryptFn& encrypt) {
    std::array<std::uint8_t, 80> msg{};
    std::copy_n(pka_x.data(), 32, msg.data());
    std::copy_n(pkb_x.data(), 32, msg.data() + 32);
    std::copy_n(nb.data(), 16, msg.data() + 64);

    const Block mac = aes_cmac(na, msg, encrypt);

    const std::uint32_t raw_val = static_cast<std::uint32_t>(mac[0]) |
                                 (static_cast<std::uint32_t>(mac[1]) << 8) |
                                 (static_cast<std::uint32_t>(mac[2]) << 16) |
                                 (static_cast<std::uint32_t>(mac[3]) << 24);

    return raw_val % 1000000U;
}

/* Захищене порівняння за сталий час (Constant-time equality) */
[[nodiscard]] bool constant_time_compare(std::span<const std::uint8_t, 16> a,
                                         std::span<const std::uint8_t, 16> b) noexcept {
    std::uint8_t diff = 0;
    for (std::size_t i = 0; i < 16; ++i) {
        diff |= static_cast<std::uint8_t>(a[i] ^ b[i]);
    }
    return diff == 0;
}

} // namespace bluetooth::crypto
