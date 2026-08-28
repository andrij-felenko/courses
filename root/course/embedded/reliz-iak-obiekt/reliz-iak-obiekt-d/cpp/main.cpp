#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>
#include <algorithm>

inline constexpr std::uint32_t fw_header_magic = 0x46574D46U;

enum class ReleaseVerifyError : std::uint8_t {
    BadMagic = 1,
    HardwareIncompatible,
    RollbackDetected,
    InvalidSignature,
    HashMismatch
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

    [[nodiscard]] constexpr std::span<const std::uint8_t, 64> header_data() const noexcept {
        return std::span<const std::uint8_t, 64>(reinterpret_cast<const std::uint8_t*>(this), 64);
    }
};
#pragma pack(pop)

class TargetBoard {
public:
    [[nodiscard]] static std::uint32_t hardware_platform_id() noexcept;
    [[nodiscard]] static std::uint8_t pcb_revision() noexcept;
    [[nodiscard]] static std::uint32_t otp_security_counter() noexcept;
    [[nodiscard]] static std::span<const std::uint8_t, 32> root_public_key() noexcept;
};

class CryptoService {
public:
    [[nodiscard]] static bool verify_signature(
        std::span<const std::uint8_t, 64> signature,
        std::span<const std::uint8_t> message,
        std::span<const std::uint8_t, 32> public_key) noexcept;

    [[nodiscard]] static std::array<std::uint8_t, 32> calculate_sha256(
        std::span<const std::uint8_t> payload) noexcept;
};

class ReleaseVerifier {
public:
    [[nodiscard]] static std::expected<void, ReleaseVerifyError> verify(
        const FirmwareHeader& header,
        std::span<const std::uint8_t> payload) noexcept {
        
        // 1. Перевірка магічного числа
        if (header.magic_word != fw_header_magic || header.header_version != 1U) {
            return std::unexpected(ReleaseVerifyError::BadMagic);
        }

        // 2. Відповідність апаратній платформі
        if (header.target_hw_id != TargetBoard::hardware_platform_id()) {
            return std::unexpected(ReleaseVerifyError::HardwareIncompatible);
        }
        const auto pcb_rev = TargetBoard::pcb_revision();
        if (pcb_rev < header.hw_rev_min || pcb_rev > header.hw_rev_max) {
            return std::unexpected(ReleaseVerifyError::HardwareIncompatible);
        }

        // 3. Захист від відкату
        if (header.security_version < TargetBoard::otp_security_counter()) {
            return std::unexpected(ReleaseVerifyError::RollbackDetected);
        }

        // 4. Перевірка цифрового підпису
        const bool sig_ok = CryptoService::verify_signature(
            header.signature,
            header.header_data(),
            TargetBoard::root_public_key()
        );
        if (!sig_ok) {
            return std::unexpected(ReleaseVerifyError::InvalidSignature);
        }

        // 5. Контроль дайджесту образу
        if (payload.size() != header.payload_size) {
            return std::unexpected(ReleaseVerifyError::HashMismatch);
        }
        const auto hash = CryptoService::calculate_sha256(payload);
        if (hash != header.payload_sha256) {
            return std::unexpected(ReleaseVerifyError::HashMismatch);
        }

        return {};
    }
};
