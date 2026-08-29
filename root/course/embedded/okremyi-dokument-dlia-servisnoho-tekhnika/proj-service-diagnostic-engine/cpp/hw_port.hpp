// hw_port.hpp — контракт плати: те, чого сервісний рушій вимагає від BSP.
#pragma once

#include <chrono>
#include <cstddef>
#include <cstdint>
#include <span>
#include <string_view>

namespace hw {

using Millis = std::chrono::milliseconds;

inline constexpr std::uint8_t RelayCount = 2;

enum class Fault : std::uint32_t {
    None        = 0,
    OverTemp    = 1u << 0,
    OverCurrent = 1u << 1,
    UnderVolt   = 1u << 2,
};

constexpr Fault operator|(Fault a, Fault b) noexcept
{
    return static_cast<Fault>(static_cast<std::uint32_t>(a) | static_cast<std::uint32_t>(b));
}
constexpr Fault& operator|=(Fault& a, Fault b) noexcept { a = a | b; return a; }
constexpr bool any(Fault f) noexcept { return f != Fault::None; }

// Монотонний час. BSP розгортає 32-бітний лічильник тіків у 64-бітний
// std::chrono, тому переповнення через 49.7 доби тут уже не існує —
// на відміну від C-версії, де кожне порівняння йде через різницю.
Millis now() noexcept;
void   delayUs(std::uint32_t us) noexcept;

std::uint32_t random() noexcept;                // апаратний TRNG
void          uartWrite(std::string_view text) noexcept; // блокуючий, не з ISR
void          setRelay(std::uint8_t channel, bool on) noexcept;
std::uint16_t adcRaw(std::uint8_t channel) noexcept;
Fault         faultFlags() noexcept;

bool eepromWrite(std::uint16_t addr, std::span<const std::byte> data) noexcept;
bool eepromRead(std::uint16_t addr, std::span<std::byte> data) noexcept;

// Софтовий I2C: обидві лінії з відкритим стоком, підтяжка зовнішня.
namespace i2c {
void sdaRelease() noexcept;
void sdaLow() noexcept;
bool sdaRead() noexcept;
void sclRelease() noexcept;
void sclLow() noexcept;
bool sclRead() noexcept;
} // namespace i2c

// Голе залізо: BSP повертає true. Під RTOS обидві реалізує rtos_task.cpp.
bool busTryLock(Millis timeout) noexcept;
void busUnlock() noexcept;

} // namespace hw
