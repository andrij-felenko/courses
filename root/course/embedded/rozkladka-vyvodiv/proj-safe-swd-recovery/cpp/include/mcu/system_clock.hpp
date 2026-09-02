#pragma once

// Безпечний запуск дерева тактування: жодне очікування готовності генератора
// не є нескінченним. Незапаяний кварц дає повільнішу прошивку, а не «цеглину».

#include <chrono>
#include <cstdint>
#include <expected>
#include <string_view>

namespace mcu {

enum class ClockSource : std::uint8_t {
    Hsi,      // внутрішній генератор напряму, 16 МГц
    HsiPll,   // PLL від внутрішнього генератора
    HsePll    // PLL від зовнішнього кварцу
};

enum class ClockError : std::uint8_t {
    PllTimeout,      // PLL не захопився
    SwitchTimeout,   // перемикач SYSCLK не прийняв джерело
    InvalidPll,      // коефіцієнти поза межами документації
    HsiDead          // не завівся навіть внутрішній генератор
};

struct PllConfig {
    std::uint32_t m;   // дільник входу VCO
    std::uint32_t n;   // множник VCO
    std::uint32_t p;   // дільник виходу на SYSCLK
    std::uint32_t q;   // дільник виходу на USB

    [[nodiscard]] constexpr std::uint32_t sysclk(std::uint32_t src_hz) const noexcept
    {
        return src_hz / m * n / p;
    }

    // Межі з документації: вхід VCO 1..2 МГц, вихід 100..432 МГц, ядро ≤ 168 МГц.
    [[nodiscard]] constexpr bool valid(std::uint32_t src_hz) const noexcept
    {
        if (m < 2 || m > 63 || n < 50 || n > 432 || q < 2 || q > 15) {
            return false;
        }
        if (p != 2 && p != 4 && p != 6 && p != 8) {
            return false;
        }
        const std::uint32_t vco_in = src_hz / m;
        const std::uint32_t vco_out = vco_in * n;
        return vco_in >= 1'000'000 && vco_in <= 2'000'000 && vco_out >= 100'000'000
            && vco_out <= 432'000'000 && vco_out / p <= 168'000'000;
    }
};

struct ClockState {
    ClockSource source;
    std::uint32_t sysclk_hz;
};

class SystemClock {
public:
    // Успіх зі source == HsiPll означає, що кварц не завівся й ми поїхали далі
    // на внутрішньому генераторі. Помилка означає відкат на голий HSI 16 МГц.
    [[nodiscard]] static std::expected<ClockState, ClockError> configure() noexcept;

    [[nodiscard]] static ClockState state() noexcept;

    static void delay(std::chrono::milliseconds d) noexcept;
};

[[nodiscard]] std::string_view to_string(ClockError error) noexcept;

}  // namespace mcu
