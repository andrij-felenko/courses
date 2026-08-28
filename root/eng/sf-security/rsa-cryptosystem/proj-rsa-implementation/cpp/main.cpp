#include <iostream>
#include <optional>
#include <stdexcept>
#include <cstdint>
#include <concepts>
#include <algorithm>
#include <span>

namespace crypto {

struct RsaPrivateKey {
    std::uint64_t n{};     // Modulus N
    std::uint64_t d{};     // Private exponent d
    std::uint64_t p{};     // Prime p
    std::uint64_t q{};     // Prime q
    std::uint64_t dp{};    // d mod (p-1)
    std::uint64_t dq{};    // d mod (q-1)
    std::uint64_t qinv{};  // q^(-1) mod p

    ~RsaPrivateKey() noexcept {
        volatile std::uint8_t* ptr = reinterpret_cast<volatile std::uint8_t*>(this);
        std::fill_n(ptr, sizeof(RsaPrivateKey), 0);
    }
};

class RsaEngine {
private:
    static constexpr std::uint64_t mul_mod(std::uint64_t a, std::uint64_t b, std::uint64_t m) noexcept {
        std::uint64_t res = 0;
        a %= m;
        while (b > 0) {
            if (b & 1) {
                res = (res + a) % m;
            }
            a = (a * 2) % m;
            b >>= 1;
        }
        return res;
    }

public:
    static constexpr std::uint64_t mod_pow(std::uint64_t base, std::uint64_t exp, std::uint64_t mod) noexcept {
        std::uint64_t result = 1;
        base %= mod;
        while (exp > 0) {
            if (exp & 1) {
                result = mul_mod(result, base, mod);
            }
            base = mul_mod(base, base, mod);
            exp >>= 1;
        }
        return result;
    }

    [[nodiscard]] static std::optional<std::uint64_t> decrypt_crt(
        std::uint64_t ciphertext, 
        const RsaPrivateKey& key) noexcept 
    {
        if (ciphertext >= key.n) {
            return std::nullopt;
        }

        const std::uint64_t cp = ciphertext % key.p;
        const std::uint64_t cq = ciphertext % key.q;

        const std::uint64_t mp = mod_pow(cp, key.dp, key.p);
        const std::uint64_t mq = mod_pow(cq, key.dq, key.q);

        const std::uint64_t diff = (mp >= mq) ? (mp - mq) : (mp + key.p - (mq % key.p));
        const std::uint64_t h = mul_mod(key.qinv, diff, key.p);

        return mq + h * key.q;
    }
};

} // namespace crypto

int main() {
    crypto::RsaPrivateKey key{
        .n = 3233, .d = 2753,
        .p = 61,   .q = 53,
        .dp = 53,  .dq = 49,
        .qinv = 38
    };

    constexpr std::uint64_t message = 65;
    constexpr std::uint64_t e = 17;

    const std::uint64_t ciphertext = crypto::RsaEngine::mod_pow(message, e, key.n);
    std::cout << "C++ RSA Encrypted: " << ciphertext << '\n';

    if (const auto decrypted = crypto::RsaEngine::decrypt_crt(ciphertext, key)) {
        std::cout << "C++ RSA Decrypted via CRT: " << *decrypted << '\n';
    }
    return 0;
}
