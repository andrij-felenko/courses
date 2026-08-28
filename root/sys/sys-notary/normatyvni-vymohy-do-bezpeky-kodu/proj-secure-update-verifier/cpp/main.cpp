#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>
#include <algorithm>

namespace cra {

constexpr uint32_t ImageMagic = 0x43524155u; // "CRAU"
constexpr uint16_t HeaderVersion = 1u;
constexpr size_t MaxImageSize = 4u * 1024u * 1024u;

constexpr uint32_t TokenSuccess = 0x5AA55AA5u;
constexpr uint32_t TokenFailure = 0xA55AA55Au;

enum class VerifyError : uint8_t {
    InvalidMagic,
    UnsupportedVersion,
    InvalidImageSize,
    RollbackViolation,
    DigestMismatch,
    SignatureInvalid,
    CryptoFailure
};

#pragma pack(push, 1)
struct ImageHeader {
    uint32_t magic;
    uint16_t header_version;
    uint16_t reserved1;
    uint32_t security_version;
    uint32_t image_size;
    std::array<uint8_t, 32> payload_sha256;
    std::array<uint8_t, 64> signature;
    std::array<uint8_t, 16> reserved2;
};
#pragma pack(pop)

// Зовнішні криптографічні функції платформи
extern "C" int crypto_sha256(const uint8_t* data, size_t len, uint8_t hash_out[32]);
extern "C" int crypto_ed25519_verify(const uint8_t sig[64], const uint8_t* msg, size_t msg_len, const uint8_t pubkey[32]);

[[nodiscard]] inline bool constant_time_equal(std::span<const uint8_t> a, std::span<const uint8_t> b) noexcept {
    if (a.size() != b.size()) return false;
    uint8_t diff = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        diff |= (a[i] ^ b[i]);
    }
    return diff == 0;
}

class FirmwareVerifier {
public:
    explicit constexpr FirmwareVerifier(std::span<const uint8_t, 32> root_public_key) noexcept
        : root_key_(root_public_key) {}

    [[nodiscard]] std::expected<void, VerifyError> verify(
        const ImageHeader& header,
        std::span<const uint8_t> payload,
        uint32_t active_security_version
    ) const noexcept {
        if (header.magic != ImageMagic) {
            return std::unexpected(VerifyError::InvalidMagic);
        }

        if (header.header_version != HeaderVersion) {
            return std::unexpected(VerifyError::UnsupportedVersion);
        }

        if (header.image_size == 0 || header.image_size > MaxImageSize || header.image_size != payload.size()) {
            return std::unexpected(VerifyError::InvalidImageSize);
        }

        // Anti-Rollback перевірка за EN 303 645 Cl. 5.3
        if (header.security_version < active_security_version) {
            return std::unexpected(VerifyError::RollbackViolation);
        }

        // Перевірка цілісності коду SHA-256
        std::array<uint8_t, 32> computed_digest{};
        if (crypto_sha256(payload.data(), payload.size(), computed_digest.data()) != 0) {
            return std::unexpected(VerifyError::CryptoFailure);
        }

        if (!constant_time_equal(computed_digest, header.payload_sha256)) {
            return std::unexpected(VerifyError::DigestMismatch);
        }

        // Перевірка підпису метаданих заголовка
        constexpr size_t signed_len = offsetof(ImageHeader, signature);
        const auto* header_bytes = reinterpret_cast<const uint8_t*>(&header);
        uint32_t verify_token = TokenFailure;

        if (crypto_ed25519_verify(header.signature.data(), header_bytes, signed_len, root_key_.data()) == 0) {
            verify_token = TokenSuccess;
        }

        if (verify_token != TokenSuccess || verify_token == TokenFailure) {
            return std::unexpected(VerifyError::SignatureInvalid);
        }

        return {};
    }

private:
    std::span<const uint8_t, 32> root_key_;
};

} // namespace cra
