// bsp_bringup.hpp — Ідіоматичний каркас безпечного запуску для C++20
#pragma once

#include <cstdint>
#include <string_view>
#include <expected>

namespace bsp {

enum class ClockSourceStatus : uint8_t {
    HsiFallback = 0,
    HseCrystal  = 1,
    ErrorTimeout = 2
};

enum class ResetCause : uint8_t {
    Unknown   = 0,
    PowerOn   = 1,
    Brownout  = 2,
    Watchdog  = 3,
    Software  = 4
};

struct HardwareHealth {
    uint32_t core_frequency_hz{0};
    ClockSourceStatus clock_status{ClockSourceStatus::HsiFallback};
    ResetCause reset_reason{ResetCause::Unknown};
    bool debugger_connected{false};
};

class BringupManager {
public:
    // Безпечний запуск системи тактування з обмеженим числом ітерацій
    [[nodiscard]] static std::expected<ClockSourceStatus, ClockSourceStatus> 
    init_clock_safe(uint32_t hse_timeout_cycles = 0x5000) noexcept;

    // Переведення плаваючих входів у безпечний аналоговий стан (енергозбереження)
    static void park_unused_pins() noexcept;

    // Неблокуюча передача рядка в доступний канал трасування (ITM/RTT/UART)
    static void log(std::string_view message) noexcept;

    // Опитування стану апаратного здоров'я плати та причин скидання
    [[nodiscard]] static HardwareHealth check_health() noexcept;
};

} // namespace bsp
