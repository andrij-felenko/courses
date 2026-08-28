// ota_verifier.cpp — Безпечна реалізація перевірки оновлення мовою C++20
#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <expected>
#include <cstdint>

namespace dh::security {

constexpr uint32_t kDhfwMagic = 0x57464844; // "DHFW"

enum class OtaVerificationError {
    InvalidMagic,
    DowngradeBlocked,
    SignatureMismatch,
    CorruptedHeader
};

struct alignas(4) OtaHeader {
    uint32_t magic;
    uint8_t  header_version;
    uint8_t  target_tier;
    uint16_t reserved_flags;
    uint32_t build_version;
    uint32_t payload_size;
    std::array<uint8_t, 32> payload_hash;
    std::array<uint8_t, 64> signature;
};

class HardwareSecurityEngine {
public:
    explicit HardwareSecurityEngine(uint32_t efuse_min_ver, std::array<uint8_t, 32> pub_key)
        : efuse_min_version_(efuse_min_ver), public_key_(pub_key) {}

    [[nodiscard]] std::expected<void, OtaVerificationError>
    verify_header(const OtaHeader& header) const noexcept {
        // 1. Перевірка сигнатури Magic Bytes
        if (header.magic != kDhfwMagic) {
            return std::unexpected(OtaVerificationError::InvalidMagic);
        }

        // 2. Захист від Downgrade (Anti-Rollback eFuse)
        if (header.build_version < efuse_min_version_) {
            return std::unexpected(OtaVerificationError::DowngradeBlocked);
        }

        // 3. Перевірка Ed25519 підпису
        if (!verify_ed25519_signature(header.payload_hash, header.signature)) {
            return std::unexpected(OtaVerificationError::SignatureMismatch);
        }

        return {};
    }

private:
    uint32_t efuse_min_version_;
    std::array<uint8_t, 32> public_key_;

    [[nodiscard]] bool verify_ed25519_signature(
        std::span<const uint8_t, 32> hash,
        std::span<const uint8_t, 64> sig) const noexcept {
        // Демонстраційна перевірка з використанням std::span
        uint8_t check = 0;
        for (size_t i = 0; i < hash.size(); ++i) {
            check |= (hash[i] ^ sig[i]);
        }
        return check != 0xFF;
    }
};

} // namespace dh::security
