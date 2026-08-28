#ifndef ML_KEM_HPP
#define ML_KEM_HPP

#include <array>
#include <span>
#include <system_error>
#include <cstdint>

namespace mlkem768 {

constexpr std::size_t PublicKeyBytes  = 1184;
constexpr std::size_t SecretKeyBytes  = 2400;
constexpr std::size_t CiphertextBytes = 1088;
constexpr std::size_t SharedSecretBytes = 32;

using PublicKey    = std::array<std::uint8_t, PublicKeyBytes>;
using SecretKey    = std::array<std::uint8_t, SecretKeyBytes>;
using Ciphertext   = std::array<std::uint8_t, CiphertextBytes>;
using SharedSecret = std::array<std::uint8_t, SharedSecretBytes>;

struct KeyPair {
    PublicKey  pk;
    SecretKey  sk;
};

struct EncapsulationResult {
    Ciphertext   ct;
    SharedSecret ss;
};

class KEM {
public:
    static KeyPair generate_keypair();
    static EncapsulationResult encapsulate(std::span<const std::uint8_t, PublicKeyBytes> pk);
    static SharedSecret decapsulate(std::span<const std::uint8_t, CiphertextBytes> ct,
                                    std::span<const std::uint8_t, SecretKeyBytes> sk);
};

} // namespace mlkem768

#endif // ML_KEM_HPP
