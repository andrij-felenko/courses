// Ідіоматичний C++20 модуль аналізу надійності заліза та скидання
#include <cstdint>
#include <string_view>
#include <expected>
#include <span>

namespace HardwareDiag {

enum class ResetCause : std::uint8_t {
    Unknown = 0,
    LowPower,
    WindowWatchdog,
    IndependentWatchdog,
    SoftwareReset,
    PowerOnReset,
    ExternalPinReset,
    BrownoutReset
};

struct DiagnosticLog {
    ResetCause cause{ResetCause::Unknown};
    std::uint32_t rawCsrRegister{0};
    bool clockSecurityFailure{false};

    [[nodiscard]] constexpr std::string_view causeToString() const noexcept {
        switch (cause) {
            case ResetCause::LowPower:            return "Low Power Reset";
            case ResetCause::WindowWatchdog:       return "Window Watchdog Reset";
            case ResetCause::IndependentWatchdog:  return "Independent Watchdog Reset";
            case ResetCause::SoftwareReset:        return "Software Reset";
            case ResetCause::PowerOnReset:         return "Power-On Reset (POR)";
            case ResetCause::ExternalPinReset:     return "External Pin Reset (NRST)";
            case ResetCause::BrownoutReset:        return "Brown-Out Reset (BOR - Power Drop)";
            case ResetCause::Unknown:
            default:                               return "Unknown Reset Source";
        }
    }
};

class SystemReliabilityMonitor {
public:
    static constexpr std::uint32_t MaskLpwr = (1UL << 31);
    static constexpr std::uint32_t MaskWwdg = (1UL << 30);
    static constexpr std::uint32_t MaskIwdg = (1UL << 29);
    static constexpr std::uint32_t MaskSft  = (1UL << 28);
    static constexpr std::uint32_t MaskPor  = (1UL << 27);
    static constexpr std::uint32_t MaskPin  = (1UL << 26);
    static constexpr std::uint32_t MaskBor  = (1UL << 25);

    [[nodiscard]] static constexpr DiagnosticLog analyzeResetState(std::uint32_t rawCsr) noexcept {
        DiagnosticLog log{};
        log.rawCsrRegister = rawCsr;

        if (rawCsr & MaskLpwr) {
            log.cause = ResetCause::LowPower;
        } else if (rawCsr & MaskWwdg) {
            log.cause = ResetCause::WindowWatchdog;
        } else if (rawCsr & MaskIwdg) {
            log.cause = ResetCause::IndependentWatchdog;
        } else if (rawCsr & MaskSft) {
            log.cause = ResetCause::SoftwareReset;
        } else if (rawCsr & MaskPor) {
            log.cause = ResetCause::PowerOnReset;
        } else if (rawCsr & MaskBor) {
            log.cause = ResetCause::BrownoutReset;
        } else if (rawCsr & MaskPin) {
            log.cause = ResetCause::ExternalPinReset;
        }

        return log;
    }

    static void handleClockSecurityEmergency() noexcept {
        // Дії безпечного стану: знеструмлення силових ключів
        // Перемикання логіки застосунку в аварійний деградований режим
    }
};

} // namespace HardwareDiag
