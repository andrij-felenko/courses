#pragma once

#include <chrono>
#include <cstddef>
#include <cstdint>
#include <span>

// Контракт із платою. BSP написаний мовою C (його дає виробник модуля), тому
// оголошення йдуть як extern "C", а поверх них — тонкі обгортки з типами,
// які не дають переплутати вивід із довжиною буфера.
namespace hal {

inline constexpr std::size_t kAxisCount = 4;
inline constexpr std::size_t kLcdCols = 128;

enum class Pin : int {
    RadioNss = 0,
    RadioBusy,
    RadioReset,
    RadioDio1,
    PowerLatch,
    RailGood
};

namespace sw {
inline constexpr std::uint16_t Arm = 0x0001;
inline constexpr std::uint16_t RateHigh = 0x0002;
inline constexpr std::uint16_t Payload = 0x0004;
inline constexpr std::uint16_t PayUp = 0x0008;
inline constexpr std::uint16_t PayDown = 0x0010;
}   // namespace sw

extern "C" {
void hal_board_init(void);
void hal_gpio_write(int pin, bool level);
bool hal_gpio_read(int pin);
void hal_spi_xfer(const std::uint8_t* tx, std::uint8_t* rx, std::size_t len);
std::uint32_t hal_micros(void);
std::uint32_t hal_millis(void);
void hal_delay_us(std::uint32_t us);
void hal_cache_invalidate(const void* addr, std::size_t len);
void hal_cache_writeback(const void* addr, std::size_t len);
const std::uint16_t* hal_adc_axes(void);
std::uint16_t hal_adc_vbat_raw(void);
std::uint16_t hal_switch_bits(void);
void hal_haptic(std::uint8_t duty);
void hal_timer_start_1khz(void (*isr)(void));
void hal_watchdog_start(std::uint32_t timeout_ms);
void hal_watchdog_kick(void);
void hal_display_page(std::uint8_t page, const std::uint8_t* cols, std::size_t len);
}

inline void init() noexcept { hal_board_init(); }
inline void write(Pin pin, bool level) noexcept { hal_gpio_write(static_cast<int>(pin), level); }
[[nodiscard]] inline bool read(Pin pin) noexcept { return hal_gpio_read(static_cast<int>(pin)); }

[[nodiscard]] inline std::chrono::microseconds now() noexcept
{
    return std::chrono::microseconds{hal_micros()};
}

inline void delay(std::chrono::microseconds d) noexcept
{
    hal_delay_us(static_cast<std::uint32_t>(d.count()));
}

// Буфер injected-АЦП: розмір відомий на етапі компіляції, тож віддаємо
// span зі статичним розширенням — довжину нікуди передавати не треба.
[[nodiscard]] inline std::span<const std::uint16_t, kAxisCount> axes() noexcept
{
    return std::span<const std::uint16_t, kAxisCount>{hal_adc_axes(), kAxisCount};
}

inline void invalidate(std::span<const std::byte> region) noexcept
{
    hal_cache_invalidate(region.data(), region.size_bytes());
}

inline void writeback(std::span<const std::byte> region) noexcept
{
    hal_cache_writeback(region.data(), region.size_bytes());
}

[[nodiscard]] inline std::uint16_t switches() noexcept { return hal_switch_bits(); }
inline void haptic(std::uint8_t duty) noexcept { hal_haptic(duty); }

inline void displayPage(std::uint8_t page, std::span<const std::byte> cols) noexcept
{
    hal_cache_writeback(cols.data(), cols.size_bytes());
    hal_display_page(page, reinterpret_cast<const std::uint8_t*>(cols.data()), cols.size());
}

}   // namespace hal
