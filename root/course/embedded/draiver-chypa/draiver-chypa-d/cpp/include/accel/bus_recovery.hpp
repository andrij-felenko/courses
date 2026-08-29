// bus_recovery.hpp — дотактовування завислої шини I2C.
//
// Мікроконтролер перезавантажився посеред читання, коли ведений тримав SDA
// притиснутою до землі. Периферія бачить постійний нуль і повертає Bus Busy
// назавжди — лікується тільки ручним тактуванням ліній.
#pragma once

#include <chrono>

#include "status.hpp"
#include "transport.hpp"

namespace accel {

inline constexpr std::chrono::microseconds kRecoveryHalfPeriod{5}; // ≈100 кГц
inline constexpr unsigned kRecoveryPulses = 9; // байт плюс такт підтвердження

template <GpioLines Lines>
[[nodiscard]] Result<void> recoverBus(Lines &lines) noexcept
{
    // Відпускаємо обидві лінії: тепер їх тримає лише той, хто завис.
    lines.sda(true);
    lines.scl(true);
    lines.delay(kRecoveryHalfPeriod);

    bool released = lines.sdaLevel();

    for (unsigned pulse = 0; pulse < kRecoveryPulses && !released; ++pulse) {
        lines.scl(false);
        lines.delay(kRecoveryHalfPeriod);
        lines.scl(true);
        lines.delay(kRecoveryHalfPeriod);
        released = lines.sdaLevel();
    }

    if (!released) {
        lines.releaseToPeripheral();
        return std::unexpected(Status::CommFail);
    }

    // Умова STOP: SDA 0→1 при високому SCL — усі чипи на шині повертаються
    // в очікування START.
    lines.sda(false);
    lines.delay(kRecoveryHalfPeriod);
    lines.scl(true);
    lines.delay(kRecoveryHalfPeriod);
    lines.sda(true);
    lines.delay(kRecoveryHalfPeriod);

    lines.releaseToPeripheral();
    return {};
}

} // namespace accel
