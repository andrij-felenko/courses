#include <cstdint>
#include <bitset>
#include <expected>
#include <span>

namespace HardwareDiag {

enum class BootFault : uint8_t {
    FlashVoltageMismatch,
    UnexpectedDownloadMode,
    InvalidStrappingPattern
};

struct BootDiagnostics {
    uint32_t rawRegisterValue{0};
    bool isSpiFlashBoot{false};
    bool isFlashVoltageNormal{true};

    [[nodiscard]] constexpr bool isHealthy() const noexcept {
        return isSpiFlashBoot && isFlashVoltageNormal;
    }
};

class StrappingSupervisor {
public:
    static constexpr uintptr_t kEsp32StrapAddress = 0x3FF44038U;

    [[nodiscard]] static std::expected<BootDiagnostics, BootFault> evaluateStartupState() noexcept {
        auto* regPtr = reinterpret_cast<volatile const uint32_t*>(kEsp32StrapAddress);
        const uint32_t rawValue = *regPtr;
        std::bitset<32> strapBits(rawValue);

        BootDiagnostics diag{};
        diag.rawRegisterValue = rawValue;
        diag.isSpiFlashBoot = strapBits.test(0);      // GPIO0 стан
        diag.isFlashVoltageNormal = !strapBits.test(5); // GPIO12 стан (0 = 3.3V)

        if (!diag.isFlashVoltageNormal) {
            return std::unexpected(BootFault::FlashVoltageMismatch);
        }

        if (!diag.isSpiFlashBoot) {
            return std::unexpected(BootFault::UnexpectedDownloadMode);
        }

        return diag;
    }
};

} // namespace HardwareDiag
