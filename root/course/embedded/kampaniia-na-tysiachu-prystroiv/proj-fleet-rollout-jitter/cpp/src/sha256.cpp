#include "sha256.hpp"

#include <algorithm>
#include <bit>
#include <cstring>

namespace fleet {
namespace {

constexpr std::array<std::uint32_t, 64> kRoundConstants{
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

constexpr std::uint32_t rotr(std::uint32_t x, int n) noexcept
{
    return std::rotr(x, n);
}

} // namespace

void Sha256::compress(const std::byte* block) noexcept
{
    std::array<std::uint32_t, 64> w{};

    for (std::size_t i = 0; i < 16; ++i) {
        w[i] = (static_cast<std::uint32_t>(block[4 * i + 0]) << 24) |
               (static_cast<std::uint32_t>(block[4 * i + 1]) << 16) |
               (static_cast<std::uint32_t>(block[4 * i + 2]) << 8) |
               (static_cast<std::uint32_t>(block[4 * i + 3]));
    }
    for (std::size_t i = 16; i < 64; ++i) {
        const std::uint32_t s0 = rotr(w[i - 15], 7) ^ rotr(w[i - 15], 18) ^ (w[i - 15] >> 3);
        const std::uint32_t s1 = rotr(w[i - 2], 17) ^ rotr(w[i - 2], 19) ^ (w[i - 2] >> 10);
        w[i] = w[i - 16] + s0 + w[i - 7] + s1;
    }

    auto [a, b, c, d, e, f, g, h] = h_;

    for (std::size_t i = 0; i < 64; ++i) {
        const std::uint32_t s1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25);
        const std::uint32_t ch = (e & f) ^ (~e & g);
        const std::uint32_t t1 = h + s1 + ch + kRoundConstants[i] + w[i];
        const std::uint32_t s0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22);
        const std::uint32_t maj = (a & b) ^ (a & c) ^ (b & c);
        const std::uint32_t t2 = s0 + maj;

        h = g; g = f; f = e;
        e = d + t1;
        d = c; c = b; b = a;
        a = t1 + t2;
    }

    const std::array<std::uint32_t, 8> add{a, b, c, d, e, f, g, h};
    for (std::size_t i = 0; i < 8; ++i) {
        h_[i] += add[i];
    }
}

void Sha256::update(std::span<const std::byte> data) noexcept
{
    bits_ += static_cast<std::uint64_t>(data.size()) * 8u;

    if (buffered_ > 0) {
        const std::size_t take = std::min(buf_.size() - buffered_, data.size());
        std::ranges::copy(data.first(take), buf_.begin() + static_cast<std::ptrdiff_t>(buffered_));
        buffered_ += take;
        data = data.subspan(take);
        if (buffered_ == buf_.size()) {
            compress(buf_.data());
            buffered_ = 0;
        }
    }

    while (data.size() >= 64) {
        compress(data.data());
        data = data.subspan(64);
    }

    std::ranges::copy(data, buf_.begin());
    buffered_ = data.size();
}

Sha256::Digest Sha256::finish() noexcept
{
    const std::uint64_t bits = bits_;

    buf_[buffered_++] = std::byte{0x80};
    if (buffered_ > 56) {
        std::fill(buf_.begin() + static_cast<std::ptrdiff_t>(buffered_), buf_.end(), std::byte{0});
        compress(buf_.data());
        buffered_ = 0;
    }
    std::fill(buf_.begin() + static_cast<std::ptrdiff_t>(buffered_),
              buf_.begin() + 56, std::byte{0});
    for (std::size_t i = 0; i < 8; ++i) {
        buf_[56 + i] = static_cast<std::byte>(bits >> (56 - 8 * i));
    }
    compress(buf_.data());

    Digest out{};
    for (std::size_t i = 0; i < 8; ++i) {
        out[4 * i + 0] = static_cast<std::byte>(h_[i] >> 24);
        out[4 * i + 1] = static_cast<std::byte>(h_[i] >> 16);
        out[4 * i + 2] = static_cast<std::byte>(h_[i] >> 8);
        out[4 * i + 3] = static_cast<std::byte>(h_[i]);
    }
    return out;
}

Sha256::Digest Sha256::of(std::span<const std::byte> first,
                          std::span<const std::byte> second) noexcept
{
    Sha256 ctx;
    ctx.update(first);
    ctx.update(second);
    return ctx.finish();
}

} // namespace fleet
