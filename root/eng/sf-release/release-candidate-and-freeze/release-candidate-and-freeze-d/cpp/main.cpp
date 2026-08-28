#include <iostream>
#include <string>
#include <string_view>
#include <expected>
#include <cstdint>
#include <format>

namespace HardwareRelease {

struct FlashConfig {
    static constexpr uint32_t FlashLimitBytes = 8912896; // 8.5 MiB
    static constexpr uint32_t RamLimitBytes = 393216;    // 384 KiB
    static constexpr uint32_t StackGuardMinBytes = 4096; // 4 KiB
};

struct ArtifactMetadata {
    uint32_t textSize{0};
    uint32_t rodataSize{0};
    uint32_t dataSize{0};
    uint32_t bssSize{0};
    uint32_t stackMinFree{0};
    uint32_t hilFailuresCount{0};
    std::string commitHash;
};

struct ValidationSuccess {
    uint32_t totalFlashUsed{0};
    uint32_t totalRamUsed{0};
    std::string summary;
};

class FirmwareValidator {
public:
    [[nodiscard]] static std::expected<ValidationSuccess, std::string>
    validate(const ArtifactMetadata& meta) noexcept {
        const uint32_t flashUsed = meta.textSize + meta.rodataSize + meta.dataSize;
        const uint32_t ramUsed = meta.dataSize + meta.bssSize;

        if (meta.hilFailuresCount > 0) {
            return std::unexpected(std::format(
                "Відхилено: виявлено {} збоїв на HIL-стендах", meta.hilFailuresCount));
        }

        if (flashUsed > FlashConfig::FlashLimitBytes) {
            return std::unexpected(std::format(
                "Перевищено ліміт Flash: {} байт > {} байт",
                flashUsed, FlashConfig::FlashLimitBytes));
        }

        if (ramUsed > FlashConfig::RamLimitBytes) {
            return std::unexpected(std::format(
                "Перевищено ліміт SRAM: {} байт > {} байт",
                ramUsed, FlashConfig::RamLimitBytes));
        }

        if (meta.stackMinFree < FlashConfig::StackGuardMinBytes) {
            return std::unexpected(std::format(
                "Критично малий стек: {} байт < {} байт запасу",
                meta.stackMinFree, FlashConfig::StackGuardMinBytes));
        }

        return ValidationSuccess{
            .totalFlashUsed = flashUsed,
            .totalRamUsed = ramUsed,
            .summary = "Образ відповідає всім апаратним лімітам пам'яті."
        };
    }
};

} // namespace HardwareRelease

int main() {
    using namespace HardwareRelease;

    ArtifactMetadata candidate{
        .textSize = 3145728,
        .rodataSize = 524288,
        .dataSize = 65536,
        .bssSize = 131072,
        .stackMinFree = 6144,
        .hilFailuresCount = 0,
        .commitHash = "7f8b2c4e1a0d9f8e7c6b5a4d3e2f1a0b9c8d7e6f"
    };

    auto result = FirmwareValidator::validate(candidate);

    if (result.has_value()) {
        const auto& success = result.value();
        std::cout << "=== ЗВІТ ВАЛІДАЦІЇ РЕЛІЗ-КАНДИДАТА (C++) ===\n";
        std::cout << "Flash ROM : " << success.totalFlashUsed << " / " << FlashConfig::FlashLimitBytes << " байт\n";
        std::cout << "SRAM      : " << success.totalRamUsed << " / " << FlashConfig::RamLimitBytes << " байт\n";
        std::cout << "Статус    : СХВАЛЕНО ДО ПРОМОЦІЇ\n";
        std::cout << "Підсумок  : " << success.summary << "\n";
        return 0;
    } else {
        std::cerr << "=== ВІДХИЛЕННЯ КАНДИДАТА ===\n";
        std::cerr << "Помилка: " << result.error() << "\n";
        return 1;
    }
}
