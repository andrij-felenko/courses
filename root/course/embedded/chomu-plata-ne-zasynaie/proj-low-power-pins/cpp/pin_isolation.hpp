// Ізоляція виводів і блоку налагодження на час сну.
//
// Правило просте: усе, що не мусить лишатися живим, іде в аналоговий режим
// без підтяжок. Список винятків приходить ззовні і має бути коротким — кожен
// зайвий вивід у ньому це мікроампери, які потім шукають амперметром.
#pragma once

#include <array>
#include <span>

#include "mcu.hpp"

namespace lowpower {

class PinIsolator {
public:
    // Список винятків не копіюється: він статичний і живе весь час роботи.
    explicit PinIsolator(std::span<const mcu::Pin> keep_awake) noexcept
        : keep_{keep_awake} {}

    // Викликається ПІСЛЯ того, як шини зупинені, а датчики знеструмлені.
    void isolate() noexcept;

    // Повертає збережену конфігурацію у зворотному порядку.
    void restore() noexcept;

    [[nodiscard]] bool isolated() const noexcept { return isolated_; }

private:
    struct PortState {
        mcu::u32 moder;
        mcu::u32 pupdr;
        mcu::u32 odr;
    };

    [[nodiscard]] mcu::u32 keep_mask(const mcu::GpioBlock& port) const noexcept;

    std::span<const mcu::Pin> keep_;
    std::array<PortState, 3> saved_{};
    bool isolated_{false};
};

} // namespace lowpower
