#include <iostream>
#include <vector>
#include <string_view>
#include <span>
#include <numeric>
#include <expected>
#include <cstdint>

namespace crypto::fiat_shamir {

constexpr uint32_t GroupP = 23;
constexpr uint32_t GroupQ = 11;
constexpr uint32_t GroupG = 4;

struct Signature {
    uint8_t alpha{0}; // Commitment α = g^r mod p
    uint8_t gamma{0}; // Response γ = (r + β * x) mod q
};

struct KeyPair {
    uint8_t secret_key{0};
    uint8_t public_key{0};
};

enum class CryptoError {
    InvalidParameter,
    SigningFailed,
    VerificationFailed
};

class SchnorrScheme {
public:
    static uint8_t mod_pow(uint32_t base, uint32_t exp, uint32_t mod) noexcept {
        uint32_t result = 1;
        base %= mod;
        while (exp > 0) {
            if (exp & 1) {
                result = (result * base) % mod;
            }
            base = (base * base) % mod;
            exp >>= 1;
        }
        return static_cast<uint8_t>(result);
    }

    static uint8_t hash_challenge(std::span<const uint8_t> message, uint8_t alpha) noexcept {
        uint32_t hash_val = 5381;
        for (uint8_t byte : message) {
            hash_val = ((hash_val << 5) + hash_val) ^ byte;
        }
        hash_val = ((hash_val << 5) + hash_val) ^ alpha;
        return static_cast<uint8_t>(hash_val % GroupQ);
    }

    static KeyPair generate_keypair() noexcept {
        uint8_t sk = 7; // Навчальний секретний ключ
        uint8_t pk = mod_pow(GroupG, sk, GroupP);
        return KeyPair{.secret_key = sk, .public_key = pk};
    }

    static std::expected<Signature, CryptoError> sign(
        std::span<const uint8_t> message,
        uint8_t secret_key
    ) noexcept {
        if (message.empty() || secret_key >= GroupQ) {
            return std::unexpected(CryptoError::InvalidParameter);
        }

        uint8_t r = 5; // Навчальна випадкова величина
        uint8_t alpha = mod_pow(GroupG, r, GroupP);
        uint8_t beta = hash_challenge(message, alpha);
        uint8_t gamma = static_cast<uint8_t>((r + beta * secret_key) % GroupQ);

        return Signature{.alpha = alpha, .gamma = gamma};
    }

    static bool verify(
        std::span<const uint8_t> message,
        uint8_t public_key,
        const Signature& sig
    ) noexcept {
        if (message.empty()) return false;

        uint8_t beta_prime = hash_challenge(message, sig.alpha);
        uint8_t lhs = mod_pow(GroupG, sig.gamma, GroupP);
        uint8_t rhs = static_cast<uint8_t>((sig.alpha * mod_pow(public_key, beta_prime, GroupP)) % GroupP);

        return (lhs == rhs);
    }
};

} // namespace crypto::fiat_shamir

int main() {
    using namespace crypto::fiat_shamir;

    auto keys = SchnorrScheme::generate_keypair();
    std::string_view msg_text = "Fiat-Shamir Transformation";
    auto msg_bytes = std::span<const uint8_t>(
        reinterpret_cast<const uint8_t*>(msg_text.data()),
        msg_text.size()
    );

    auto sig_result = SchnorrScheme::sign(msg_bytes, keys.secret_key);
    if (!sig_result) {
        std::cerr << "Помилка підписання повідомлення\n";
        return 1;
    }

    const auto& sig = *sig_result;
    std::cout << "Сформовано підпис Фіата — Шаміра (C++20):\n"
              << "  α = " << static_cast<int>(sig.alpha) << "\n"
              << "  γ = " << static_cast<int>(sig.gamma) << "\n";

    bool valid = SchnorrScheme::verify(msg_bytes, keys.public_key, sig);
    std::cout << "Статус верифікації: " << (valid ? "УСПІХ" : "ПОМИЛКА") << "\n";

    return valid ? 0 : 1;
}
