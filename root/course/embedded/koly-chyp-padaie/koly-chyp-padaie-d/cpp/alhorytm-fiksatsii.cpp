#include <cstdint>
#include <type_traits>
#include "stm32f4xx.h"

namespace system::diagnostic {

enum class ResetCause : uint32_t {
    Unknown      = 0,
    PowerOn      = (1 << 0),
    Brownout     = (1 << 1),
    PinReset     = (1 << 2),
    WatchdogInd  = (1 << 3),
    WatchdogWin  = (1 << 4),
    Software     = (1 << 5),
    LowPower     = (1 << 6)
};

[[nodiscard]] constexpr ResetCause operator|(ResetCause a, ResetCause b) noexcept {
    return static_cast<ResetCause>(
        static_cast<uint32_t>(a) | static_cast<uint32_t>(b)
    );
}

[[nodiscard]] inline ResetCause capture_and_clear_reset_cause() noexcept {
    const uint32_t csr = RCC->CSR;
    auto cause = ResetCause::Unknown;

    if (csr & RCC_CSR_LPWRRSTF) cause = cause | ResetCause::LowPower;
    if (csr & RCC_CSR_WWDGRSTF) cause = cause | ResetCause::WatchdogWin;
    if (csr & RCC_CSR_IWDGRSTF) cause = cause | ResetCause::WatchdogInd;
    if (csr & RCC_CSR_SFTRSTF)  cause = cause | ResetCause::Software;
    if (csr & RCC_CSR_PORRSTF)  cause = cause | ResetCause::PowerOn;
    if (csr & RCC_CSR_PINRSTF)  cause = cause | ResetCause::PinReset;
    if (csr & RCC_CSR_BORRSTF)  cause = cause | ResetCause::Brownout;

    // Очищення липких прапорців для наступного життєвого циклу
    RCC->CSR |= RCC_CSR_RMVF;

    return cause;
}

} // namespace system::diagnostic
