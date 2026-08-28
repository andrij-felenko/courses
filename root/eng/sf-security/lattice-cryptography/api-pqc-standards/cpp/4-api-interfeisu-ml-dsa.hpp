#ifndef ML_DSA_HPP
#define ML_DSA_HPP

#include <array>
#include <span>
#include <system_error>
#include <cstdint>

namespace mldsa65 {

constexpr std::size_t PublicKeyBytes = 1952;
constexpr std::size_t SecretKeyBytes = 4032;
constexpr std::size_t SignatureBytes = 3309;

using PublicKey = std::array<std::uint8_t, PublicKeyBytes>;
using SecretKey = std::array<std::uint8_t, SecretKeyBytes>;
using Signature = std::array<std::uint8_t, SignatureBytes>;

struct KeyPair {
    PublicKey pk;
    SecretKey sk;
};

class DigitalSignature {
public:
    static KeyPair generate_keypair();
    static Signature sign(std::span<const std::uint8_t> message,
                          std::span<const std::uint8_t, SecretKeyBytes> sk);
    static bool verify(std::span<const std::uint8_t> message,
                       std::span<const std::uint8_t, SignatureBytes> signature,
                       std::span<const std::uint8_t, PublicKeyBytes> pk);
};

} // namespace mldsa65

#endif // ML_DSA_HPP
