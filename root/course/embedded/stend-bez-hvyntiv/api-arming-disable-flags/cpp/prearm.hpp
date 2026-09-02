#pragma once

#include "arming_flags.hpp"

#include <chrono>
#include <cstdint>

namespace bf {

using Millis = std::chrono::milliseconds;

// Пороги — типові значення прошивки за замовчуванням.
inline constexpr Millis kFailsafeDelay{400};   // failsafe_delay = 4 (десяті секунди)
inline constexpr Millis kRxRecovery{1000};     // захисна секунда чистого лінка
inline constexpr std::uint16_t kMinCheckUs = 1050;
inline constexpr std::uint16_t kRcMinUs = 1000;
inline constexpr std::uint16_t kRcMaxUs = 2000;
inline constexpr std::uint8_t kCpuLoadLimitPercent = 75;
inline constexpr std::uint8_t kGpsMinSats = 6;

// Зріз того, що модулі апарата повідомляють диспетчеру в одному такті.
// Значення за замовчуванням описують справний стенд, тож сценарій
// задає лише те, що зламано.
struct StandInputs {
    bool gyroPresent{true};
    bool accCalibrated{true};
    bool gyroCalibrating{false};

    bool rxFrameValid{true};       // у цьому такті приймач віддав валідний кадр
    bool rxFailsafeFlag{false};    // приймач сам підняв свій failsafe
    bool boxFailsafe{false};
    std::uint16_t throttleUs{1000};
    std::uint16_t rollUs{1500};
    std::uint16_t pitchUs{1500};
    bool armSwitchHigh{false};
    bool prearmRequired{false};
    bool prearmEngaged{false};

    bool cliOpen{false};
    bool mspClientActive{false};
    bool motorTestActive{false};
    bool cmsMenuOpen{false};
    bool osdMenuOpen{false};

    bool servosSettling{false};
    bool motorProtocolOk{true};
    bool rpmFilterEnabled{false};
    bool escTelemetryOk{true};

    bool paralyze{false};
    bool rescueSwitch{false};
    bool rebootRequired{false};
    bool gpsRequired{false};
    std::uint8_t gpsSats{0};
    std::uint8_t cpuLoadPercent{30};
};

// Те, що прошивка пам'ятає МІЖ тактами: таймери радіолінка
// і засувка тумблера армінгу.
class PrearmMonitor {
public:
    PrearmMonitor(const StandInputs& atBoot, Millis now);

    [[nodiscard]] Mask update(const StandInputs& in, Millis now);

private:
    void updateLink(const StandInputs& in, Millis now);

    bool linkOk_;
    Millis linkOkSince_;
    Millis linkLostSince_;
    bool failsafe_;
    bool armSwitchLatched_;
};

}  // namespace bf
