#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>
#include <algorithm>

enum class VerifyError : std::uint8_t {
    MagicMismatch = 1,
    HardwareMismatch,
    RollbackDetected,
    InvalidSignature,
    PayloadHashMismatch
};

#pragma pack(push, 1)
struct FirmwareHeader {
    std::uint32_t magic_word;
    std::uint32_t header_version;
    std::uint32_t target_hw_id;
    std::uint8_t  hw_rev_min;
    std::uint8_t  hw_rev_max;
    std::uint16_t flags;
    std::uint8_t  ver_major;
    std::uint8_t  ver_minor;
    std::uint8_t  ver_patch;
    std::uint8_t  ver_pre_flags;
    std::uint32_t security_version;
    std::uint32_t payload_size;
    std::uint32_t load_address;
    std::array<std::uint8_t, 32> payload_sha256;
    std::array<std::uint8_t, 64> signature;

    [[nodiscard]] constexpr std::span<const std::uint8_t, 64> signed_region() const noexcept {
        return std::span<const std::uint8_t, 64>(reinterpret_cast<const std::uint8_t*>(this), 64);
    }
};
#pragma pack(pop)

class HardwarePlatform {
public:
    [[nodiscard]] static std::uint32_t hardware_id() noexcept;
    [[nodiscard]] static std::uint8_t board_revision() noexcept;
    [[nodiscard]] static std::uint32_t security_version() noexcept;
    [[nodiscard]] static std::span<const std::uint8_t, 32> root_public_key() noexcept;
};

class CryptoEngine {
public:
    [[nodiscard]] static bool verify_ed25519(
        std::span<const std::uint8_t, 64> signature,
        std::span<const std::uint8_t> message,
        std::span<const std::uint8_t, 32> public_key) noexcept;

    [[nodiscard]] static std::array<std::uint8_t, 32> calculate_sha256(
        std::span<const std::uint8_t> data) noexcept;
};

class ImageVerifier {
public:
    [[nodiscard]] static std::expected<void, VerifyError> verify(
        const FirmwareHeader& header,
        std::span<const std::uint8_t> payload) noexcept {
        
        // 1. Перевірка валідності сигнатури структури
        if (header.magic_word != 0x46574D46U || header.header_version != 1U) {
            return std::unexpected(VerifyError::MagicMismatch);
        }

        // 2. Відповідність цільової апаратної платформи
        if (header.target_hw_id != HardwarePlatform::hardware_id()) {
            return std::unexpected(VerifyError::HardwareMismatch);
        }
        const auto rev = HardwarePlatform::board_revision();
        if (rev < header.hw_rev_min || rev > header.hw_rev_max) {
            return std::unexpected(VerifyError::HardwareMismatch);
        }

        // 3. Контроль відкату версії безпеки
        if (header.security_version < HardwarePlatform::security_version()) {
            return std::unexpected(VerifyError::RollbackDetected);
        }

        // 4. Перевірка підпису заголовка
        const bool sig_valid = CryptoEngine::verify_ed25519(
            header.signature,
            header.signed_region(),
            HardwarePlatform::root_public_key()
        );
        if (!sig_valid) {
            return std::unexpected(VerifyError::InvalidSignature);
        }

        // 5. Цілісність образу
        if (payload.size() != header.payload_size) {
            return std::unexpected(VerifyError::PayloadHashMismatch);
        }
        const auto actual_hash = CryptoEngine::calculate_sha256(payload);
        if (actual_hash != header.payload_sha256) {
            return std::unexpected(VerifyError::PayloadHashMismatch);
        }

        return {};
    }
};
