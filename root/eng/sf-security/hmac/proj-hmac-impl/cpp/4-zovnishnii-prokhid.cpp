#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <span>
#include <string_view>

namespace crypto {

constexpr size_t sha256_block_size = 64;
constexpr size_t sha256_digest_size = 32;

class Sha256 {
public:
    Sha256() noexcept { reset(); }

    void reset() noexcept {
        state_ = {0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
                  0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19};
        count_ = 0;
        buffer_.fill(0);
    }

    void update(std::span<const uint8_t> data) noexcept {
        size_t buf_idx = static_cast<size_t>(count_ % sha256_block_size);
        count_ += data.size();
        size_t offset = 0;
        size_t remaining = data.size();

        while (remaining > 0) {
            size_t copy_len = sha256_block_size - buf_idx;
            if (remaining < copy_len) copy_len = remaining;
            std::memcpy(&buffer_[buf_idx], &data[offset], copy_len);
            offset += copy_len;
            remaining -= copy_len;
            buf_idx = (buf_idx + copy_len) % sha256_block_size;
            if (buf_idx == 0) {
                transform(buffer_.data());
            }
        }
    }

    void update(std::string_view str) noexcept {
        update(std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(str.data()), str.size()));
    }

    [[nodiscard]] std::array<uint8_t, sha256_digest_size> finalize() noexcept {
        std::array<uint8_t, 64> pad = {0x80};
        uint64_t bitlen = count_ * 8;
        std::array<uint8_t, 8> len_bytes{};
        for (size_t i = 0; i < 8; ++i) {
            len_bytes[7 - i] = static_cast<uint8_t>(bitlen >> (i * 8));
        }

        size_t rem = count_ % 64;
        size_t pad_len = (rem < 56) ? (56 - rem) : (120 - rem);
        update(std::span<const uint8_t>(pad.data(), pad_len));
        update(std::span<const uint8_t>(len_bytes.data(), 8));

        std::array<uint8_t, sha256_digest_size> digest{};
        for (size_t i = 0; i < 8; ++i) {
            digest[i * 4]     = static_cast<uint8_t>(state_[i] >> 24);
            digest[i * 4 + 1] = static_cast<uint8_t>(state_[i] >> 16);
            digest[i * 4 + 2] = static_cast<uint8_t>(state_[i] >> 8);
            digest[i * 4 + 3] = static_cast<uint8_t>(state_[i]);
        }
        return digest;
    }

    static std::array<uint8_t, sha256_digest_size> hash(std::span<const uint8_t> data) noexcept {
        Sha256 ctx;
        ctx.update(data);
        return ctx.finalize();
    }

private:
    static constexpr uint32_t rotr(uint32_t x, uint32_t n) noexcept {
        return (x >> n) | (x << (32 - n));
    }
    static constexpr uint32_t ch(uint32_t x, uint32_t y, uint32_t z) noexcept { return (x & y) ^ (~x & z); }
    static constexpr uint32_t maj(uint32_t x, uint32_t y, uint32_t z) noexcept { return (x & y) ^ (x & z) ^ (y & z); }
    static constexpr uint32_t ep0(uint32_t x) noexcept { return rotr(x, 2) ^ rotr(x, 13) ^ rotr(x, 22); }
    static constexpr uint32_t ep1(uint32_t x) noexcept { return rotr(x, 6) ^ rotr(x, 11) ^ rotr(x, 25); }
    static constexpr uint32_t sig0(uint32_t x) noexcept { return rotr(x, 7) ^ rotr(x, 18) ^ (x >> 3); }
    static constexpr uint32_t sig1(uint32_t x) noexcept { return rotr(x, 17) ^ rotr(x, 19) ^ (x >> 10); }

    void transform(const uint8_t data[64]) noexcept {
        static constexpr std::array<uint32_t, 64> k256 = {
            0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
            0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
            0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
            0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
            0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
            0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
            0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
            0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
        };

        std::array<uint32_t, 64> w{};
        for (size_t i = 0; i < 16; ++i) {
            w[i] = (static_cast<uint32_t>(data[i * 4]) << 24) |
                   (static_cast<uint32_t>(data[i * 4 + 1]) << 16) |
                   (static_cast<uint32_t>(data[i * 4 + 2]) << 8) |
                   (static_cast<uint32_t>(data[i * 4 + 3]));
        }
        for (size_t i = 16; i < 64; ++i) {
            w[i] = sig1(w[i - 2]) + w[i - 7] + sig0(w[i - 15]) + w[i - 16];
        }

        uint32_t a = state_[0], b = state_[1], c = state_[2], d = state_[3];
        uint32_t e = state_[4], f = state_[5], g = state_[6], h = state_[7];

        for (size_t i = 0; i < 64; ++i) {
            uint32_t t1 = h + ep1(e) + ch(e, f, g) + k256[i] + w[i];
            uint32_t t2 = ep0(a) + maj(a, b, c);
            h = g; g = f; f = e; e = d + t1;
            d = c; c = b; b = a; a = t1 + t2;
        }

        state_[0] += a; state_[1] += b; state_[2] += c; state_[3] += d;
        state_[4] += e; state_[5] += f; state_[6] += g; state_[7] += h;
    }

    std::array<uint32_t, 8> state_{};
    uint64_t count_{0};
    std::array<uint8_t, sha256_block_size> buffer_{};
};

class HmacSha256 {
public:
    explicit HmacSha256(std::span<const uint8_t> key) noexcept {
        std::array<uint8_t, sha256_block_size> k_prime{};
        if (key.size() > sha256_block_size) {
            auto hashed_key = Sha256::hash(key);
            std::copy(hashed_key.begin(), hashed_key.end(), k_prime.begin());
        } else {
            std::copy(key.begin(), key.end(), k_prime.begin());
        }

        std::array<uint8_t, sha256_block_size> k_ipad{};
        std::array<uint8_t, sha256_block_size> k_opad{};
        for (size_t i = 0; i < sha256_block_size; ++i) {
            k_ipad[i] = k_prime[i] ^ 0x36;
            k_opad[i] = k_prime[i] ^ 0x5C;
        }

        inner_.update(k_ipad);
        outer_.update(k_opad);

        // Очищення чутливих ключів зі стеку
        k_prime.fill(0);
        k_ipad.fill(0);
        k_opad.fill(0);
    }

    void update(std::span<const uint8_t> data) noexcept {
        inner_.update(data);
    }

    void update(std::string_view str) noexcept {
        inner_.update(str);
    }

    [[nodiscard]] std::array<uint8_t, sha256_digest_size> finalize() noexcept {
        auto inner_digest = inner_.finalize();
        outer_.update(inner_digest);
        auto final_tag = outer_.finalize();
        inner_digest.fill(0);
        return final_tag;
    }

    static std::array<uint8_t, sha256_digest_size> sign(
        std::span<const uint8_t> key,
        std::span<const uint8_t> data) noexcept {
        HmacSha256 hmac(key);
        hmac.update(data);
        return hmac.finalize();
    }

private:
    Sha256 inner_;
    Sha256 outer_;
};

} // namespace crypto
