#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>

namespace bootloader {

constexpr uint32_t ManifestMagic = 0x5346574D; // "SFWM"
constexpr size_t MaxKeySlots = 4;
constexpr size_t HashSizeBytes = 32;
constexpr size_t SignatureSizeBytes = 64;
constexpr size_t PublicKeySizeBytes = 32;

enum class Status : uint8_t {
    Ok = 0,
    InvalidMagic,
    InvalidSlot,
    KeyRevoked,
    RootMismatch,
    RollbackDetected,
    SignatureInvalid,
    BufferTooShort
};

using HashArray = std::array<uint8_t, HashSizeBytes>;
using PublicKeyArray = std::array<uint8_t, PublicKeySizeBytes>;
using SignatureArray = std::array<uint8_t, SignatureSizeBytes>;

#pragma pack(push, 1)
struct FirmwareManifest {
    uint32_t magic;
    uint32_t payloadLength;
    uint32_t securityVersion;
    uint8_t  keySlotIndex;
    uint8_t  reserved[3];
    PublicKeyArray publicKey;
    SignatureArray signature;
};
#pragma pack(pop)

struct EfuseState {
    std::array<HashArray, MaxKeySlots> rootKeyDigests;
    uint8_t revocationMask;
    uint32_t monotonicCounter;
};

// Безпечне порівняння двох блоків за сталий час
[[nodiscard]] constexpr bool constantTimeEqual(std::span<const uint8_t> a, std::span<const uint8_t> b) noexcept {
    if (a.size() != b.size()) {
        return false;
    }
    uint8_t diff = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        diff |= (a[i] ^ b[i]);
    }
    return diff == 0;
}

// Абстракція над апаратними крипторушіями
class CryptoEngine {
public:
    static HashArray sha256(std::span<const uint8_t> data) noexcept;
    static bool verifyEd25519(
        std::span<const uint8_t, PublicKeySizeBytes> pubKey,
        std::span<const uint8_t, HashSizeBytes> msgHash,
        std::span<const uint8_t, SignatureSizeBytes> signature
    ) noexcept;
};

class HardwareSecurityController {
public:
    static bool burnRevocationBit(uint8_t slotIndex) noexcept;
    static bool burnMonotonicCounter(uint32_t newCounter) noexcept;
};

class SecureBootVerifier {
public:
    [[nodiscard]] static std::expected<void, Status> verifyAndStage(
        const FirmwareManifest& manifest,
        std::span<const uint8_t> payload,
        const EfuseState& efuse,
        bool shouldCommitRotation
    ) noexcept {
        // 1. Перевірка заголовка
        if (manifest.magic != ManifestMagic) {
            return std::unexpected(Status::InvalidMagic);
        }

        // 2. Валідація індексу слота
        if (manifest.keySlotIndex >= MaxKeySlots) {
            return std::unexpected(Status::InvalidSlot);
        }

        // 3. Перевірка біта відкликання в eFuse
        const uint8_t slotMask = static_cast<uint8_t>(1U << manifest.keySlotIndex);
        if ((efuse.revocationMask & slotMask) != 0) {
            return std::unexpected(Status::KeyRevoked);
        }

        // 4. Порівняння хешу відкритого ключа з еталоном Root of Trust
        const HashArray computedKeyDigest = CryptoEngine::sha256(manifest.publicKey);
        if (!constantTimeEqual(computedKeyDigest, efuse.rootKeyDigests[manifest.keySlotIndex])) {
            return std::unexpected(Status::RootMismatch);
        }

        // 5. Захист від відкату
        if (manifest.securityVersion < efuse.monotonicCounter) {
            return std::unexpected(Status::RollbackDetected);
        }

        // 6. Перевірка цифрового підпису образу
        const HashArray payloadHash = CryptoEngine::sha256(payload.first(manifest.payloadLength));
        if (!CryptoEngine::verifyEd25519(manifest.publicKey, payloadHash, manifest.signature)) {
            return std::unexpected(Status::SignatureInvalid);
        }

        // 7. Безпечна фіксація ротації
        if (shouldCommitRotation) {
            for (uint8_t slot = 0; slot < manifest.keySlotIndex; ++slot) {
                if ((efuse.revocationMask & (1U << slot)) == 0) {
                    HardwareSecurityController::burnRevocationBit(slot);
                }
            }

            if (manifest.securityVersion > efuse.monotonicCounter) {
                HardwareSecurityController::burnMonotonicCounter(manifest.securityVersion);
            }
        }

        return {};
    }
};

} // namespace bootloader
