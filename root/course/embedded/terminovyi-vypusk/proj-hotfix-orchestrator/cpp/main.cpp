#include "emergency_fw_header.hpp"
#include <cstring>
#include <span>
#include <expected>

// Апаратні зовнішні API платформи
extern "C" uint32_t hw_efuse_read_security_version();
extern "C" uint32_t hw_get_platform_id();
extern "C" bool crypto_sha256(const uint8_t* data, uint32_t len, uint8_t* out_hash);
extern "C" bool crypto_verify_signature(const uint8_t* pubkey, const uint8_t* hash, const uint8_t* sig);

namespace emergency {

class FirmwareValidator {
public:
    explicit FirmwareValidator(std::span<const uint8_t> rootPublicKey)
        : rootPublicKey_(rootPublicKey) {}

    [[nodiscard]] std::expected<void, ValidationError> validate(
        const Header& header,
        std::span<const uint8_t> payload
    ) const noexcept {
        // 1. Перевірка магічного числа
        if (header.magic != HeaderMagic) {
            return std::unexpected(ValidationError::BadMagic);
        }

        // 2. Перевірка версії заголовка
        if (header.headerVersion != CurrentHeaderVersion) {
            return std::unexpected(ValidationError::UnsupportedVersion);
        }

        // 3. Звірка ідентифікатора апаратури
        if (header.targetHwId != hw_get_platform_id()) {
            return std::unexpected(ValidationError::HardwareMismatch);
        }

        // 4. Захист від відкату версії безпеки
        const uint32_t activeSecurityVersion = hw_efuse_read_security_version();
        if (header.securityCounter < activeSecurityVersion) {
            return std::unexpected(ValidationError::RollbackBlocked);
        }

        // 5. Перевірка розміру тіла прошивки
        if (header.payloadSize != payload.size()) {
            return std::unexpected(ValidationError::PayloadBounds);
        }

        // 6. Обчислення SHA-256 корисного навантаження
        uint8_t calculatedSha[Sha256SizeBytes];
        if (!crypto_sha256(payload.data(), static_cast<uint32_t>(payload.size()), calculatedSha)) {
            return std::unexpected(ValidationError::HashMismatch);
        }

        if (std::memcmp(calculatedSha, header.payloadSha256, Sha256SizeBytes) != 0) {
            return std::unexpected(ValidationError::HashMismatch);
        }

        // 7. Верифікація криптографічного підпису заголовка
        uint8_t headerHash[Sha256SizeBytes];
        constexpr size_t SignedBytes = sizeof(Header) - SignatureSizeBytes - sizeof(Header::reserved);

        if (!crypto_sha256(reinterpret_cast<const uint8_t*>(&header), static_cast<uint32_t>(SignedBytes), headerHash)) {
            return std::unexpected(ValidationError::SignatureInvalid);
        }

        if (!crypto_verify_signature(rootPublicKey_.data(), headerHash, header.headerSignature)) {
            return std::unexpected(ValidationError::SignatureInvalid);
        }

        return {};
    }

private:
    std::span<const uint8_t> rootPublicKey_;
};

} // namespace emergency
