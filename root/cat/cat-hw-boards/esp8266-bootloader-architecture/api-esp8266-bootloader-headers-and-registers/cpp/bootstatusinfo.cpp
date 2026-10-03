#include <cstdint>

struct BootStatusInfo {
    std::uint8_t resetReason;
    std::uint8_t gpioModeVal;

    [[nodiscard]] constexpr bool isFlashBoot() const noexcept {
        return gpioModeVal == 3U;
    }

    [[nodiscard]] constexpr bool isDownloadMode() const noexcept {
        return gpioModeVal == 1U;
    }
};

class BootLogAnalyzer {
public:
    static constexpr BootStatusInfo decode(std::uint8_t rstCause, std::uint8_t bootModeX) noexcept {
        return BootStatusInfo{rstCause, bootModeX};
    }
};
