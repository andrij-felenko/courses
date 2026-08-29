#include "sha256.hpp"

#include <algorithm>
#include <bit>
#include <cstring>

namespace upkg {
namespace {

constexpr std::uint32_t ch(std::uint32_t x, std::uint32_t y, std::uint32_t z) {
    return (x & y) ^ (~x & z);
}
constexpr std::uint32_t maj(std::uint32_t x, std::uint32_t y, std::uint32_t z) {
    return (x & y) ^ (x & z) ^ (y & z);
}
constexpr std::uint32_t bsig0(std::uint32_t x) {
    return std::rotr(x, 2) ^ std::rotr(x, 13) ^ std::rotr(x, 22);
}
constexpr std::uint32_t bsig1(std::uint32_t x) {
    return std::rotr(x, 6) ^ std::rotr(x, 11) ^ std::rotr(x, 25);
}
constexpr std::uint32_t ssig0(std::uint32_t x) {
    return std::rotr(x, 7) ^ std::rotr(x, 18) ^ (x >> 3);
}
constexpr std::uint32_t ssig1(std::uint32_t x) {
    return std::rotr(x, 17) ^ std::rotr(x, 19) ^ (x >> 10);
}

constexpr std::array<std::uint32_t, 64> kRound{
    0x428a2f98u, 0x71374491u, 0xb5c0fbcfu, 0xe9b5dba5u,
    0x3956c25bu, 0x59f111f1u, 0x923f82a4u, 0xab1c5ed5u,
    0xd807aa98u, 0x12835b01u, 0x243185beu, 0x550c7dc3u,
    0x72be5d74u, 0x80deb1feu, 0x9bdc06a7u, 0xc19bf174u,
    0xe49b69c1u, 0xefbe4786u, 0x0fc19dc6u, 0x240ca1ccu,
    0x2de92c6fu, 0x4a7484aau, 0x5cb0a9dcu, 0x76f988dau,
    0x983e5152u, 0xa831c66du, 0xb00327c8u, 0xbf597fc7u,
    0xc6e00bf3u, 0xd5a79147u, 0x06ca6351u, 0x14292967u,
    0x27b70a85u, 0x2e1b2138u, 0x4d2c6dfcu, 0x53380d13u,
    0x650a7354u, 0x766a0abbu, 0x81c2c92eu, 0x92722c85u,
    0xa2bfe8a1u, 0xa81a664bu, 0xc24b8b70u, 0xc76c51a3u,
    0xd192e819u, 0xd6990624u, 0xf40e3585u, 0x106aa070u,
    0x19a4c116u, 0x1e376c08u, 0x2748774cu, 0x34b0bcb5u,
    0x391c0cb3u, 0x4ed8aa4au, 0x5b9cca4fu, 0x682e6ff3u,
    0x748f82eeu, 0x78a5636fu, 0x84c87814u, 0x8cc70208u,
    0x90befffau, 0xa4506cebu, 0xbef9a3f7u, 0xc67178f2u};

}  // namespace

void Sha256::compress(const std::uint8_t* block) noexcept {
    std::array<std::uint32_t, 64> w{};
    for (std::size_t i = 0; i < 16; ++i) {
        w[i] = (static_cast<std::uint32_t>(block[i * 4 + 0]) << 24) |
               (static_cast<std::uint32_t>(block[i * 4 + 1]) << 16) |
               (static_cast<std::uint32_t>(block[i * 4 + 2]) << 8) |
               (static_cast<std::uint32_t>(block[i * 4 + 3]));
    }
    for (std::size_t i = 16; i < 64; ++i) {
        w[i] = ssig1(w[i - 2]) + w[i - 7] + ssig0(w[i - 15]) + w[i - 16];
    }

    auto s = state_;
    for (std::size_t i = 0; i < 64; ++i) {
        const std::uint32_t t1 =
            s[7] + bsig1(s[4]) + ch(s[4], s[5], s[6]) + kRound[i] + w[i];
        const std::uint32_t t2 = bsig0(s[0]) + maj(s[0], s[1], s[2]);
        s[7] = s[6]; s[6] = s[5]; s[5] = s[4]; s[4] = s[3] + t1;
        s[3] = s[2]; s[2] = s[1]; s[1] = s[0]; s[0] = t1 + t2;
    }
    for (std::size_t i = 0; i < state_.size(); ++i) {
        state_[i] += s[i];
    }
}

void Sha256::update(std::span<const std::uint8_t> data) noexcept {
    bit_len_ += static_cast<std::uint64_t>(data.size()) * 8;

    // Добираємо хвіст попереднього виклику до повного блоку.
    if (fill_ > 0) {
        const std::size_t take = std::min(kBlockSize - fill_, data.size());
        std::copy_n(data.begin(), take, block_.begin() + fill_);
        fill_ += take;
        data = data.subspan(take);
        if (fill_ < kBlockSize) {
            return;
        }
        compress(block_.data());
        fill_ = 0;
    }

    while (data.size() >= kBlockSize) {
        compress(data.data());
        data = data.subspan(kBlockSize);
    }

    if (!data.empty()) {
        std::copy(data.begin(), data.end(), block_.begin());
        fill_ = data.size();
    }
}

Sha256::Digest Sha256::finish() noexcept {
    const std::uint64_t bit_len = bit_len_;

    // Доповнення: 0x80, нулі, і 8 байтів довжини в бітах.
    block_[fill_++] = 0x80;
    if (fill_ > kBlockSize - 8) {
        std::fill(block_.begin() + fill_, block_.end(), std::uint8_t{0});
        compress(block_.data());
        fill_ = 0;
    }
    std::fill(block_.begin() + fill_, block_.end() - 8, std::uint8_t{0});
    for (std::size_t i = 0; i < 8; ++i) {
        block_[kBlockSize - 1 - i] =
            static_cast<std::uint8_t>(bit_len >> (8 * i));
    }
    compress(block_.data());

    Digest out{};
    for (std::size_t i = 0; i < state_.size(); ++i) {
        out[i * 4 + 0] = static_cast<std::uint8_t>(state_[i] >> 24);
        out[i * 4 + 1] = static_cast<std::uint8_t>(state_[i] >> 16);
        out[i * 4 + 2] = static_cast<std::uint8_t>(state_[i] >> 8);
        out[i * 4 + 3] = static_cast<std::uint8_t>(state_[i]);
    }

    // Стан більше не потрібен — не лишаємо його в пам'яті.
    state_.fill(0);
    block_.fill(0);
    bit_len_ = 0;
    fill_ = 0;
    return out;
}

}  // namespace upkg
