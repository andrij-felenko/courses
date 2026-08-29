#include "sha256.hpp"

#include <algorithm>
#include <bit>
#include <cassert>

namespace fw {
namespace {

constexpr std::array<std::uint32_t, 64> round_constants{
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

[[nodiscard]] constexpr std::uint32_t ch(std::uint32_t x, std::uint32_t y, std::uint32_t z) noexcept
{
    return (x & y) ^ (~x & z);
}

[[nodiscard]] constexpr std::uint32_t maj(std::uint32_t x, std::uint32_t y, std::uint32_t z) noexcept
{
    return (x & y) ^ (x & z) ^ (y & z);
}

/* std::rotr із <bit> — рівно та інструкція ROR, яку хочеться бачити
   на Cortex-M, і без ручного трюку зі зсувами в обидва боки. */
[[nodiscard]] constexpr std::uint32_t big_sigma0(std::uint32_t x) noexcept
{
    return std::rotr(x, 2) ^ std::rotr(x, 13) ^ std::rotr(x, 22);
}

[[nodiscard]] constexpr std::uint32_t big_sigma1(std::uint32_t x) noexcept
{
    return std::rotr(x, 6) ^ std::rotr(x, 11) ^ std::rotr(x, 25);
}

[[nodiscard]] constexpr std::uint32_t small_sigma0(std::uint32_t x) noexcept
{
    return std::rotr(x, 7) ^ std::rotr(x, 18) ^ (x >> 3);
}

[[nodiscard]] constexpr std::uint32_t small_sigma1(std::uint32_t x) noexcept
{
    return std::rotr(x, 17) ^ std::rotr(x, 19) ^ (x >> 10);
}

}  // namespace

/* w[64] — це 256 байтів стека; для завантажувача з двома кілобайтами
   прийнятно, але знати про це треба. */
void Sha256::compress(const std::byte* block) noexcept
{
    std::array<std::uint32_t, 64> w{};

    for (std::size_t i = 0; i < 16; ++i) {
        w[i] = (static_cast<std::uint32_t>(block[4 * i + 0]) << 24) |
               (static_cast<std::uint32_t>(block[4 * i + 1]) << 16) |
               (static_cast<std::uint32_t>(block[4 * i + 2]) << 8)  |
               (static_cast<std::uint32_t>(block[4 * i + 3]));
    }
    for (std::size_t i = 16; i < 64; ++i) {
        w[i] = small_sigma1(w[i - 2]) + w[i - 7] + small_sigma0(w[i - 15]) + w[i - 16];
    }

    auto [a, b, c, d, e, f, g, h] = state_;

    for (std::size_t i = 0; i < 64; ++i) {
        const std::uint32_t t1 = h + big_sigma1(e) + ch(e, f, g) + round_constants[i] + w[i];
        const std::uint32_t t2 = big_sigma0(a) + maj(a, b, c);
        h = g; g = f; f = e; e = d + t1;
        d = c; c = b; b = a; a = t1 + t2;
    }

    const std::array<std::uint32_t, 8> delta{a, b, c, d, e, f, g, h};
    for (std::size_t i = 0; i < 8; ++i) {
        state_[i] += delta[i];
    }
}

void Sha256::update(std::span<const std::byte> data) noexcept
{
    assert(!finished_ && "після finish() об'єкт повторно не вживається");

    total_bits_ += static_cast<std::uint64_t>(data.size()) * 8u;

    /* Спершу добиваємо недобраний хвіст попереднього виклику. */
    if (used_ > 0) {
        const std::size_t need = std::min(64 - used_, data.size());
        std::ranges::copy(data.first(need), block_.begin() + used_);
        used_ += need;
        data = data.subspan(need);
        if (used_ == 64) {
            compress(block_.data());
            used_ = 0;
        }
    }

    /* Цілі блоки жують просто з вхідного буфера, без копіювання. */
    while (data.size() >= 64) {
        compress(data.data());
        data = data.subspan(64);
    }

    if (!data.empty()) {
        std::ranges::copy(data, block_.begin());
        used_ = data.size();
    }
}

Digest Sha256::finish() noexcept
{
    assert(!finished_);
    finished_ = true;

    const std::uint64_t bits = total_bits_;

    /* Доповнення: байт 0x80, нулі до зсуву 56, далі 64-бітна довжина в бітах
       старшим байтом уперед. Не лишилось місця під довжину — ще один блок. */
    block_[used_++] = std::byte{0x80};
    if (used_ > 56) {
        std::ranges::fill(std::span{block_}.subspan(used_), std::byte{0});
        compress(block_.data());
        used_ = 0;
    }
    std::ranges::fill(std::span{block_}.subspan(used_, 56 - used_), std::byte{0});
    for (std::size_t i = 0; i < 8; ++i) {
        block_[56 + i] = static_cast<std::byte>(bits >> (56 - 8 * i));
    }
    compress(block_.data());

    Digest digest{};
    for (std::size_t i = 0; i < 8; ++i) {
        digest[4 * i + 0] = static_cast<std::byte>(state_[i] >> 24);
        digest[4 * i + 1] = static_cast<std::byte>(state_[i] >> 16);
        digest[4 * i + 2] = static_cast<std::byte>(state_[i] >> 8);
        digest[4 * i + 3] = static_cast<std::byte>(state_[i]);
    }

    /* Робочі буфери затираємо: вони переживуть повернення з функції,
       а лишати чужі байти в RAM перед стрибком у застосунок — погана звичка. */
    state_.fill(0);
    block_.fill(std::byte{0});
    return digest;
}

}  // namespace fw
