#include "hmac_sha256.hpp"

#include <algorithm>

namespace secure {
namespace {

constexpr std::array<std::uint32_t, 64> kRoundConstants = {
    0x428a2f98U, 0x71374491U, 0xb5c0fbcfU, 0xe9b5dba5U,
    0x3956c25bU, 0x59f111f1U, 0x923f82a4U, 0xab1c5ed5U,
    0xd807aa98U, 0x12835b01U, 0x243185beU, 0x550c7dc3U,
    0x72be5d74U, 0x80deb1feU, 0x9bdc06a7U, 0xc19bf174U,
    0xe49b69c1U, 0xefbe4786U, 0x0fc19dc6U, 0x240ca1ccU,
    0x2de92c6fU, 0x4a7484aaU, 0x5cb0a9dcU, 0x76f988daU,
    0x983e5152U, 0xa831c66dU, 0xb00327c8U, 0xbf597fc7U,
    0xc6e00bf3U, 0xd5a79147U, 0x06ca6351U, 0x14292967U,
    0x27b70a85U, 0x2e1b2138U, 0x4d2c6dfcU, 0x53380d13U,
    0x650a7354U, 0x766a0abbU, 0x81c2c92eU, 0x92722c85U,
    0xa2bfe8a1U, 0xa81a664bU, 0xc24b8b70U, 0xc76c51a3U,
    0xd192e819U, 0xd6990624U, 0xf40e3585U, 0x106aa070U,
    0x19a4c116U, 0x1e376c08U, 0x2748774cU, 0x34b0bcb5U,
    0x391c0cb3U, 0x4ed8aa4aU, 0x5b9cca4fU, 0x682e6ff3U,
    0x748f82eeU, 0x78a5636fU, 0x84c87814U, 0x8cc70208U,
    0x90befffaU, 0xa4506cebU, 0xbef9a3f7U, 0xc67178f2U
};

constexpr std::uint32_t rotr(std::uint32_t x, unsigned n) noexcept {
    return (x >> n) | (x << (32U - n));
}

constexpr std::uint32_t ch(std::uint32_t x, std::uint32_t y, std::uint32_t z) noexcept {
    return (x & y) ^ (~x & z);
}

constexpr std::uint32_t maj(std::uint32_t x, std::uint32_t y, std::uint32_t z) noexcept {
    return (x & y) ^ (x & z) ^ (y & z);
}

constexpr std::uint32_t bsig0(std::uint32_t x) noexcept { return rotr(x, 2) ^ rotr(x, 13) ^ rotr(x, 22); }
constexpr std::uint32_t bsig1(std::uint32_t x) noexcept { return rotr(x, 6) ^ rotr(x, 11) ^ rotr(x, 25); }
constexpr std::uint32_t ssig0(std::uint32_t x) noexcept { return rotr(x, 7) ^ rotr(x, 18) ^ (x >> 3); }
constexpr std::uint32_t ssig1(std::uint32_t x) noexcept { return rotr(x, 17) ^ rotr(x, 19) ^ (x >> 10); }

/* Слова стану читаються й пишуться побайтово: блок може лежати за
 * невирівняною адресою DMA-буфера, а порядок байтів у SHA-256 старший-перший. */
constexpr std::uint32_t load_be32(const std::uint8_t* p) noexcept {
    return (static_cast<std::uint32_t>(p[0]) << 24) | (static_cast<std::uint32_t>(p[1]) << 16)
         | (static_cast<std::uint32_t>(p[2]) << 8)  |  static_cast<std::uint32_t>(p[3]);
}

constexpr void store_be32(std::uint8_t* p, std::uint32_t v) noexcept {
    p[0] = static_cast<std::uint8_t>(v >> 24);
    p[1] = static_cast<std::uint8_t>(v >> 16);
    p[2] = static_cast<std::uint8_t>(v >> 8);
    p[3] = static_cast<std::uint8_t>(v);
}

}  // namespace

Sha256::~Sha256() noexcept {
    ScopedWipe::wipe(buf_);
    h_.fill(0);
    total_len_ = 0;
    buf_len_ = 0;
}

void Sha256::reset() noexcept {
    h_ = {0x6a09e667U, 0xbb67ae85U, 0x3c6ef372U, 0xa54ff53aU,
          0x510e527fU, 0x9b05688cU, 0x1f83d9abU, 0x5be0cd19U};
    buf_.fill(0);
    total_len_ = 0;
    buf_len_ = 0;
}

/*
 * Розклад повідомлення тримаємо в кільці з шістнадцяти слів замість масиву на
 * 64: 64 байти стеку проти 256. На Cortex-M0 з кількома кілобайтами RAM саме
 * це вирішує, чи влізе перевірка в стек мережевого завдання.
 */
void Sha256::compress(const std::uint8_t* block) noexcept {
    /* Перший блок HMAC — це ключ, змішаний з ipad, тож розклад повідомлення
     * теж секрет: страж затре його на виході зі скоупа. */
    std::array<std::uint32_t, 16> w{};
    ScopedWipe guard{std::span<std::uint8_t>{reinterpret_cast<std::uint8_t*>(w.data()), sizeof(w)}};

    std::uint32_t a = h_[0], b = h_[1], c = h_[2], d = h_[3];
    std::uint32_t e = h_[4], f = h_[5], g = h_[6], h = h_[7];

    for (unsigned i = 0; i < 64U; ++i) {
        std::uint32_t wi;
        if (i < 16U) {
            wi = load_be32(block + 4U * i);
            w[i] = wi;
        } else {
            /* W[i] = SSIG1(W[i-2]) + W[i-7] + SSIG0(W[i-15]) + W[i-16] */
            wi = w[i & 15U] + ssig0(w[(i + 1U) & 15U])
               + w[(i + 9U) & 15U] + ssig1(w[(i + 14U) & 15U]);
            w[i & 15U] = wi;
        }

        const std::uint32_t t1 = h + bsig1(e) + ch(e, f, g) + kRoundConstants[i] + wi;
        const std::uint32_t t2 = bsig0(a) + maj(a, b, c);

        h = g; g = f; f = e; e = d + t1;
        d = c; c = b; b = a; a = t1 + t2;
    }

    h_[0] += a; h_[1] += b; h_[2] += c; h_[3] += d;
    h_[4] += e; h_[5] += f; h_[6] += g; h_[7] += h;
}

void Sha256::update(std::span<const std::uint8_t> data) noexcept {
    total_len_ += data.size();

    /* Добираємо хвіст попереднього виклику до повного блоку. */
    if (buf_len_ != 0) {
        const std::size_t take = std::min(kBlockSize - buf_len_, data.size());
        std::copy_n(data.begin(), take, buf_.begin() + static_cast<std::ptrdiff_t>(buf_len_));
        buf_len_ += take;
        data = data.subspan(take);
        if (buf_len_ < kBlockSize) {
            return;                     /* блок ще не повний */
        }
        compress(buf_.data());
        buf_len_ = 0;
    }

    /* Повні блоки беремо просто з вхідного буфера, без проміжного копіювання. */
    while (data.size() >= kBlockSize) {
        compress(data.data());
        data = data.subspan(kBlockSize);
    }

    std::copy(data.begin(), data.end(), buf_.begin());
    buf_len_ = data.size();
}

Sha256::Digest Sha256::finish() noexcept {
    const std::uint64_t bit_len = total_len_ * 8U;

    /* Доповнення: одиничний біт, нулі, 64-бітна довжина в бітах у хвості. */
    buf_[buf_len_++] = 0x80U;
    if (buf_len_ > kBlockSize - 8U) {
        std::fill(buf_.begin() + static_cast<std::ptrdiff_t>(buf_len_), buf_.end(), 0U);
        compress(buf_.data());
        buf_len_ = 0;
    }
    std::fill(buf_.begin() + static_cast<std::ptrdiff_t>(buf_len_),
              buf_.begin() + static_cast<std::ptrdiff_t>(kBlockSize - 8U), 0U);
    store_be32(buf_.data() + kBlockSize - 8U, static_cast<std::uint32_t>(bit_len >> 32));
    store_be32(buf_.data() + kBlockSize - 4U, static_cast<std::uint32_t>(bit_len));
    compress(buf_.data());

    Digest out{};
    for (std::size_t i = 0; i < 8U; ++i) {
        store_be32(out.data() + 4U * i, h_[i]);
    }

    reset();                            /* стан більше не потрібен нікому */
    return out;
}

Sha256::Digest Sha256::hash(std::span<const std::uint8_t> data) noexcept {
    Sha256 ctx;
    ctx.update(data);
    return ctx.finish();
}

Sha256::Digest hmac_sha256(std::span<const std::uint8_t> key,
                           std::span<const std::uint8_t> msg) noexcept {
    constexpr std::uint8_t kIpad = 0x36U;
    constexpr std::uint8_t kOpad = 0x5cU;

    std::array<std::uint8_t, Sha256::kBlockSize> k0{};
    std::array<std::uint8_t, Sha256::kBlockSize> pad{};
    ScopedWipe k0_guard{k0};            /* обидва буфери тримають ключ — */
    ScopedWipe pad_guard{pad};          /* деструктори заберуть їх зі стеку */

    if (key.size() > Sha256::kBlockSize) {
        const auto folded = Sha256::hash(key);
        std::copy(folded.begin(), folded.end(), k0.begin());
    } else {
        std::copy(key.begin(), key.end(), k0.begin());
    }

    /* Внутрішній прохід: SHA256((K0 ^ ipad) || msg) */
    std::transform(k0.begin(), k0.end(), pad.begin(),
                   [](std::uint8_t b) { return static_cast<std::uint8_t>(b ^ kIpad); });
    Sha256 inner_ctx;
    inner_ctx.update(pad);
    inner_ctx.update(msg);
    const Sha256::Digest inner = inner_ctx.finish();

    /* Зовнішній прохід: SHA256((K0 ^ opad) || inner) */
    std::transform(k0.begin(), k0.end(), pad.begin(),
                   [](std::uint8_t b) { return static_cast<std::uint8_t>(b ^ kOpad); });
    Sha256 outer_ctx;
    outer_ctx.update(pad);
    outer_ctx.update(inner);
    return outer_ctx.finish();
}

}  // namespace secure
