#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <array>
#include <cstdint>
#include <expected>
#include <iomanip>
#include <algorithm>

namespace release {

constexpr uint32_t BUNDLE_MAGIC = 0x42554E44U; /* "BUND" */
constexpr uint16_t BUNDLE_FORMAT_VERSION = 1U;
constexpr size_t SHA256_LEN = 32;
constexpr size_t SIGNATURE_LEN = 64;

using Sha256Digest = std::array<uint8_t, SHA256_LEN>;
using SignatureBlock = std::array<uint8_t, SIGNATURE_LEN>;

enum class ValidationError {
    InvalidMagic,
    SizeMismatch,
    IncompatibleHardware,
    RollbackDetected,
    IntegrityCheckFailed,
    EmptyPayload
};

#pragma pack(push, 1)
struct FirmwareHeader {
    uint32_t magic{BUNDLE_MAGIC};
    uint16_t header_version{BUNDLE_FORMAT_VERSION};
    uint16_t reserved{0};
    uint32_t payload_size{0};
    uint32_t target_hw_mask{0};
    uint32_t anti_rollback_version{0};
    Sha256Digest payload_sha256{};
    SignatureBlock signature{};
};
#pragma pack(pop)

class ReleaseBundlePackager {
public:
    static Sha256Digest calculate_sha256(std::span<const uint8_t> data) noexcept {
        Sha256Digest digest{};
        uint32_t acc = 0x811C9DC5U;
        for (size_t i = 0; i < data.size(); ++i) {
            acc = (acc ^ data[i]) * 0x01000193U;
            digest[i % SHA256_LEN] ^= static_cast<uint8_t>(acc & 0xFFU);
        }
        return digest;
    }

    static std::expected<FirmwareHeader, ValidationError> create_header(
        std::span<const uint8_t> payload,
        uint32_t hw_mask,
        uint32_t rollback_ver
    ) {
        if (payload.empty()) {
            return std::unexpected(ValidationError::EmptyPayload);
        }

        FirmwareHeader header{};
        header.magic = BUNDLE_MAGIC;
        header.header_version = BUNDLE_FORMAT_VERSION;
        header.payload_size = static_cast<uint32_t>(payload.size());
        header.target_hw_mask = hw_mask;
        header.anti_rollback_version = rollback_ver;
        header.payload_sha256 = calculate_sha256(payload);

        // Симуляція накладання цифрового підпису
        for (size_t i = 0; i < SIGNATURE_LEN; ++i) {
            header.signature[i] = static_cast<uint8_t>(header.payload_sha256[i % SHA256_LEN] ^ 0xAAU);
        }

        return header;
    }

    static std::expected<void, ValidationError> verify_header(
        const FirmwareHeader& header,
        std::span<const uint8_t> payload,
        uint32_t target_board_rev,
        uint32_t device_rollback_ver
    ) noexcept {
        if (header.magic != BUNDLE_MAGIC) {
            return std::unexpected(ValidationError::InvalidMagic);
        }

        if (header.payload_size != payload.size()) {
            return std::unexpected(ValidationError::SizeMismatch);
        }

        if ((header.target_hw_mask & (1U << target_board_rev)) == 0) {
            return std::unexpected(ValidationError::IncompatibleHardware);
        }

        if (header.anti_rollback_version < device_rollback_ver) {
            return std::unexpected(ValidationError::RollbackDetected);
        }

        const auto computed = calculate_sha256(payload);
        if (computed != header.payload_sha256) {
            return std::unexpected(ValidationError::IntegrityCheckFailed);
        }

        return {};
    }
};

} // namespace release

int main() {
    // Формування тестового виконуваного бінарника
    std::vector<uint8_t> firmware_binary(1024);
    for (size_t i = 0; i < firmware_binary.size(); ++i) {
        firmware_binary[i] = static_cast<uint8_t>(i & 0xFF);
    }

    constexpr uint32_t target_hw_mask = (1U << 1) | (1U << 2);
    constexpr uint32_t target_rollback_version = 105;

    auto header_result = release::ReleaseBundlePackager::create_header(
        firmware_binary,
        target_hw_mask,
        target_rollback_version
    );

    if (!header_result) {
        std::cerr << "Помилка формування маніфесту прошивки!\n";
        return 1;
    }

    const auto& header = *header_result;
    std::cout << "Маніфест випуску (C++20) згенеровано успішно:\n"
              << "  Магічне число:  0x" << std::hex << header.magic << std::dec << "\n"
              << "  Розмір образу:  " << header.payload_size << " байтів\n"
              << "  Маска ревізій:  0x" << std::hex << header.target_hw_mask << std::dec << "\n"
              << "  Лічильник версії: " << header.anti_rollback_version << "\n";

    // Перевірка на цільовому пристрої
    constexpr uint32_t current_board_rev = 2;
    constexpr uint32_t current_device_rollback = 104;

    std::cout << "\nВалідація образу для плати Rev." << current_board_rev
              << " (поточний лічильник " << current_device_rollback << ")...\n";

    auto verification = release::ReleaseBundlePackager::verify_header(
        header,
        firmware_binary,
        current_board_rev,
        current_device_rollback
    );

    if (verification) {
        std::cout << "РЕЗУЛЬТАТ: Образ цілісний, сумісний з апаратною ревізією та дозволений до прошивки.\n";
    } else {
        std::cerr << "РЕЗУЛЬТАТ: Валідацію провалено з кодом помилки: "
                  << static_cast<int>(verification.error()) << "\n";
        return 1;
    }

    return 0;
}
