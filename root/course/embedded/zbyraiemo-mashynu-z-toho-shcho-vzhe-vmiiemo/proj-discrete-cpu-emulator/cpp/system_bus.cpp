#include "system_bus.hpp"

#include <algorithm>
#include <format>
#include <iostream>
#include <stdexcept>
#include <type_traits>

namespace emu {

void SystemBus::load_rom(std::span<const std::uint8_t> image)
{
    if (image.size() > rom_.size()) {
        throw std::length_error(
            std::format("образ на {} байтів не влазить у ROM ({} байтів)",
                        image.size(), rom_.size()));
    }
    rom_.fill(0);
    std::ranges::copy(image, rom_.begin());
}

void SystemBus::report_ghost(std::uint16_t addr, const MmioReg& reg) const
{
    if (reg.ghost && trace_) {
        std::cout << std::format("  [ALIAS] 0x{:04X} — фантомна копія 0x{:04X} (дешифровано лише A0)\n",
                                 addr, static_cast<std::uint16_t>(kMmioBase | reg.index));
    }
}

std::uint8_t SystemBus::read_mmio(std::uint16_t addr, const MmioReg& reg)
{
    if (reg.index == 0) {
        // Зворотне читання засувки: порт віддає записане значення,
        // а не напругу, яка справді стоїть на ніжці.
        if (trace_) {
            std::cout << std::format("  [BUS RD] MMIO 0x{:04X} (GPIO_OUT, зворотне читання) = 0x{:02X}\n",
                                     addr, gpio_out_latch_);
        }
        return gpio_out_latch_;
    }

    ++button_polls_;
    if (button_polls_ > press_after_) {
        gpio_in_pins_ &= static_cast<std::uint8_t>(~0x01);  // кнопку натиснуто: ніжка на землі
    }
    if (trace_) {
        std::cout << std::format("  [BUS RD] MMIO 0x{:04X} (GPIO_IN, опитування {}) = 0x{:02X} -> кнопка {}\n",
                                 addr, button_polls_, gpio_in_pins_,
                                 (gpio_in_pins_ & 0x01) ? "відпущена" : "НАТИСНУТА");
    }
    return gpio_in_pins_;
}

std::expected<void, BusFault> SystemBus::write_mmio(std::uint16_t addr, const MmioReg& reg, std::uint8_t data)
{
    if (reg.index != 0) {
        return std::unexpected(BusFault::ReadOnlyRegister);
    }

    gpio_out_latch_ = data;
    if (trace_) {
        std::cout << std::format("  [BUS WR] MMIO 0x{:04X} (GPIO_OUT) = 0x{:02X} -> Світлодіод: {}\n",
                                 addr, data, led_on() ? "УВІМКНЕНО (3.3 В)" : "ВИМКНЕНО (0 В)");
    }
    return {};
}

std::expected<std::uint8_t, BusFault> SystemBus::read(std::uint16_t addr)
{
    ++cycles_;

    return std::visit([&](const auto& target) -> std::expected<std::uint8_t, BusFault> {
        using T = std::decay_t<decltype(target)>;

        if constexpr (std::is_same_v<T, RomCell>) {
            return rom_[target.offset];
        } else if constexpr (std::is_same_v<T, RamCell>) {
            return ram_[target.offset];
        } else if constexpr (std::is_same_v<T, MmioReg>) {
            report_ghost(addr, target);
            return read_mmio(addr, target);
        } else {
            return std::unexpected(BusFault::NoDevice);
        }
    }, decode_address(addr));
}

std::expected<void, BusFault> SystemBus::write(std::uint16_t addr, std::uint8_t data)
{
    ++cycles_;

    return std::visit([&](const auto& target) -> std::expected<void, BusFault> {
        using T = std::decay_t<decltype(target)>;

        if constexpr (std::is_same_v<T, RomCell>) {
            // Кристал програм навіть не має входу запису — цикл нікуди не дійде.
            return std::unexpected(BusFault::RomWrite);
        } else if constexpr (std::is_same_v<T, RamCell>) {
            ram_[target.offset] = data;
            if (trace_) {
                std::cout << std::format("  [BUS WR] SRAM 0x{:04X} = 0x{:02X}\n", addr, data);
            }
            return {};
        } else if constexpr (std::is_same_v<T, MmioReg>) {
            report_ghost(addr, target);
            return write_mmio(addr, target, data);
        } else {
            return std::unexpected(BusFault::NoDevice);
        }
    }, decode_address(addr));
}

std::uint8_t SystemBus::peek(std::uint16_t addr) const noexcept
{
    return std::visit([&](const auto& target) -> std::uint8_t {
        using T = std::decay_t<decltype(target)>;

        if constexpr (std::is_same_v<T, RomCell>) {
            return rom_[target.offset];
        } else if constexpr (std::is_same_v<T, RamCell>) {
            return ram_[target.offset];
        } else if constexpr (std::is_same_v<T, MmioReg>) {
            return target.index == 0 ? gpio_out_latch_ : gpio_in_pins_;
        } else {
            return kOpenBus;
        }
    }, decode_address(addr));
}

std::uint8_t SystemBus::ram_at(std::uint16_t addr) const noexcept
{
    const auto target = decode_address(addr);
    if (const auto* cell = std::get_if<RamCell>(&target)) {
        return ram_[cell->offset];
    }
    return kOpenBus;
}

void SystemBus::press_button_after(unsigned polls) noexcept
{
    press_after_   = polls;
    button_polls_  = 0;
    gpio_in_pins_ |= 0x01;   // кнопку відпустили
}

}  // namespace emu
