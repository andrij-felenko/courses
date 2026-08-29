// shadow_registers.hpp — тіньові копії конфігураційних регістрів в ОЗП.
//
// Прямий Read-Modify-Write по шині скидає прапорці регістрів clear-on-read,
// нищить регістри лише для запису й затирає заводські біти калібрування.
// Тому поточне значення береться з тіні, а тінь оновлюється лише після
// підтвердженого запису.
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>

#include "registers.hpp"

namespace accel {

class ShadowBank {
public:
    // Порядок збігається з порядком повернення конфігурації після скидання
    // шини: спершу діапазон і BDU, потім осі, потім переривання й буфер.
    static constexpr std::array<regs::Reg, 5> order{
        regs::Reg::Ctrl4, regs::Reg::Ctrl1, regs::Reg::Ctrl3,
        regs::Reg::FifoCtrl, regs::Reg::Ctrl5};

    [[nodiscard]] static constexpr std::optional<std::size_t> indexOf(regs::Reg reg) noexcept
    {
        for (std::size_t i = 0; i < order.size(); ++i) {
            if (order[i] == reg) {
                return i;
            }
        }
        return std::nullopt;
    }

    [[nodiscard]] constexpr std::uint8_t value(regs::Reg reg) const noexcept
    {
        const auto index = indexOf(reg);
        return index ? cells_[*index] : std::uint8_t{0};
    }

    constexpr void store(regs::Reg reg, std::uint8_t value) noexcept
    {
        if (const auto index = indexOf(reg)) {
            cells_[*index] = value;
        }
    }

private:
    std::array<std::uint8_t, order.size()> cells_{};
};

} // namespace accel
