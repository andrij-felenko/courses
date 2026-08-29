#pragma once

#include <cstdint>
#include <expected>

/*
 * Тактове дерево: кварц 8 МГц -> PLL -> SYSCLK 168 МГц.
 * Помилка повертається як std::expected, а не кодом -1: пропустити її
 * мовчки не вийде, бо результат позначено [[nodiscard]].
 */

namespace bsp::clock {

enum class Error : std::uint8_t {
    hse_timeout,        // кварц не розгойдався
    hsi_timeout,        // не піднявся навіть внутрішній RC
    pll_timeout,        // контур не захопив фазу
    switch_timeout,     // мультиплексор SYSCLK не підтвердив перемикання
    voltage_timeout,    // регулятор ядра не вийшов на рівень
    flash_latency       // контролер Flash не прийняв нову затримку
};

enum class VoltageScale : std::uint32_t {
    scale3 = 0b01,      // найощадніший режим, до 120 МГц
    scale2 = 0b10,
    scale1 = 0b11       // 1.2 В — потрібно для 168 МГц
};

using Result = std::expected<void, Error>;

inline constexpr std::uint32_t hsi_hz = 16'000'000;
inline constexpr std::uint32_t hse_hz = 8'000'000;
inline constexpr std::uint32_t pll_hz = 168'000'000;

inline constexpr std::uint32_t flash_ws_168mhz = 5;
inline constexpr std::uint32_t flash_ws_16mhz  = 0;
inline constexpr std::uint32_t timeout_cycles  = 0x5000;

/* Коефіцієнти контуру рахуються й перевіряються на етапі компіляції:
   помилковий дільник тут не доживе до плати */
struct PllSettings {
    std::uint32_t m;
    std::uint32_t n;
    std::uint32_t p;
    std::uint32_t q;

    constexpr std::uint32_t pfd_hz(std::uint32_t src) const noexcept { return src / m; }
    constexpr std::uint32_t vco_hz(std::uint32_t src) const noexcept { return pfd_hz(src) * n; }
    constexpr std::uint32_t out_hz(std::uint32_t src) const noexcept { return vco_hz(src) / p; }
    constexpr std::uint32_t usb_hz(std::uint32_t src) const noexcept { return vco_hz(src) / q; }

    constexpr bool valid(std::uint32_t src) const noexcept {
        return m >= 2 && m <= 63
            && n >= 50 && n <= 432
            && (p == 2 || p == 4 || p == 6 || p == 8)
            && q >= 2 && q <= 15
            && pfd_hz(src) >= 1'000'000 && pfd_hz(src) <= 2'000'000
            && vco_hz(src) >= 100'000'000 && vco_hz(src) <= 432'000'000
            && out_hz(src) <= 168'000'000
            && usb_hz(src) == 48'000'000;
    }

    /* Готове слово RCC_PLLCFGR: P кодується як (P/2 - 1), джерело — HSE */
    constexpr std::uint32_t encode_from_hse() const noexcept {
        return (m << 0) | (n << 6) | (((p / 2) - 1) << 16) | (1U << 22) | (q << 24);
    }
};

inline constexpr PllSettings pll168{.m = 4, .n = 168, .p = 2, .q = 7};

static_assert(pll168.valid(hse_hz), "коефіцієнти PLL виходять за межі з даташита");
static_assert(pll168.out_hz(hse_hz) == pll_hz, "SYSCLK вийшов не 168 МГц");
static_assert(pll168.usb_hz(hse_hz) == 48'000'000, "шина USB лишилася без 48 МГц");

[[nodiscard]] Result configure_pll_168mhz() noexcept;

/* Аварійне зведення дерева на внутрішній RC 16 МГц */
void fallback_to_hsi() noexcept;

[[nodiscard]] Result set_flash_latency(std::uint32_t wait_states) noexcept;
[[nodiscard]] Result set_voltage_scale(VoltageScale scale) noexcept;
void reset_flash_caches() noexcept;
void set_bus_prescalers(std::uint32_t ahb, std::uint32_t apb1, std::uint32_t apb2) noexcept;

std::uint32_t sysclk_hz() noexcept;
void note_sysclk(std::uint32_t hz) noexcept;

/* Скільки разів CSS ловив зрив кварцу; лічильник переживає скидання */
std::uint32_t css_event_count() noexcept;

[[noreturn]] void system_reset() noexcept;

} // namespace bsp::clock
