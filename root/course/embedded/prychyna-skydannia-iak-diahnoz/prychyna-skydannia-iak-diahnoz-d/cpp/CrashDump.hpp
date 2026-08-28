// CrashDump.hpp — об'єктно-орієнтований діагностичний інтерфейс
#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <string_view>
#include <array>

namespace Fault {

enum class ResetCause : uint32_t {
    Unknown     = 0,
    ColdBoot    = 1,
    Brownout    = 2,
    Watchdog    = 3,
    Software    = 4,
    PinReset    = 5,
    HardFault   = 6
};

struct alignas(4) CrashRecord {
    static constexpr uint32_t MagicValue = 0x43525348U; // 'CRSH'
    static constexpr size_t StackWordsCount = 16;

    uint32_t magic{0};
    uint32_t rawRccCsr{0};
    ResetCause cause{ResetCause::Unknown};
    uint32_t uptimeMs{0};

    // Стековий кадр ARM Cortex-M
    uint32_t r0{0};
    uint32_t r1{0};
    uint32_t r2{0};
    uint32_t r3{0};
    uint32_t r12{0};
    uint32_t lr{0};
    uint32_t pc{0};
    uint32_t xpsr{0};

    // Діагностичні регістри SCB
    uint32_t cfsr{0};
    uint32_t hfsr{0};
    uint32_t bfar{0};
    uint32_t mmfar{0};
    uint32_t excReturn{0};

    std::array<uint32_t, StackWordsCount> stackDump{};
    std::array<char, 32> assertFile{};
    uint32_t assertLine{0};

    uint32_t crc32{0};
};

class BlackBox {
public:
    static void earlyInit() noexcept;
    [[nodiscard]] static bool hasValidRecord() noexcept;
    [[nodiscard]] static const CrashRecord& getRecord() noexcept;
    static void clear() noexcept;
    
    static void reportAssert(std::string_view file, uint32_t line) noexcept;
    [[nodiscard]] static constexpr std::string_view causeToString(ResetCause cause) noexcept;

private:
    static uint32_t calculateCrc32(std::span<const uint8_t> data) noexcept;
};

constexpr std::string_view BlackBox::causeToString(ResetCause cause) noexcept {
    switch (cause) {
        case ResetCause::ColdBoot:  return "Power-On Reset (Cold Boot)";
        case ResetCause::Brownout:  return "Brown-Out Voltage Dip (BOR)";
        case ResetCause::Watchdog:  return "Watchdog Timeout (IWDG/WWDG)";
        case ResetCause::Software:  return "Software Reset / Assert";
        case ResetCause::PinReset:  return "External Pin Reset (NRST)";
        case ResetCause::HardFault: return "Hardware Exception (HardFault)";
        default:                    return "Unknown Reset Cause";
    }
}

} // namespace Fault
