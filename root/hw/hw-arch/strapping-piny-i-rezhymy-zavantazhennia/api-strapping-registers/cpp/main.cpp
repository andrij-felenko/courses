#include <cstdint>
#include <bitset>
#include <expected>
#include <span>

namespace SystemDiagnostic {

enum class BootTarget : uint8_t {
    SpiFlashNormal,
    UartDownloadMode,
    SdioSlaveMode,
    Unknown
};

enum class HardwareError : uint8_t {
    FlashVoltageBrownout1V8,
    UnexpectedDownloadMode,
    InvalidBusConfiguration
};

struct StartupReport {
    uint32_t rawValue{0};
    BootTarget target{BootTarget::Unknown};
    bool flashVoltage1V8{false};
    bool romLogEnabled{false};

    [[nodiscard]] constexpr bool isSafeForProduction() const noexcept {
        return (target == BootTarget::SpiFlashNormal) && (!flashVoltage1V8);
    }
};

class StrappingDiagnostic {
public:
    static constexpr uintptr_t kEsp32StrapRegister = 0x3FF44038U;

    [[nodiscard]] static std::expected<StartupReport, HardwareError> evaluateSystemHealth() noexcept {
        auto* regAddress = reinterpret_cast<volatile const uint32_t*>(kEsp32StrapRegister);
        const uint32_t raw = *regAddress;
        std::bitset<32> bits(raw);

        StartupReport report{};
        report.rawValue = raw;
        report.flashVoltage1V8 = bits.test(5);
        report.romLogEnabled = bits.test(1);

        const bool gpio0 = bits.test(0);
        const bool gpio2 = bits.test(2);

        if (gpio0) {
            report.target = BootTarget::SpiFlashNormal;
        } else if (!gpio2) {
            report.target = BootTarget::UartDownloadMode;
        } else {
            report.target = BootTarget::SdioSlaveMode;
        }

        if (report.flashVoltage1V8) {
            return std::unexpected(HardwareError::FlashVoltageBrownout1V8);
        }

        if (report.target != BootTarget::SpiFlashNormal) {
            return std::unexpected(HardwareError::UnexpectedDownloadMode);
        }

        return report;
    }
};

} // namespace SystemDiagnostic
