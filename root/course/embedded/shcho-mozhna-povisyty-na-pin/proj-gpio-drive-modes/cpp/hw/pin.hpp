// pin.hpp — один вивід як тип. Порт і номер відомі під час компіляції, тож
// звертання до регістра згортається в кілька інструкцій, а невірний номер
// піна не доживає до прошивки.
#pragma once

#include "mcu.hpp"

#include <expected>
#include <type_traits>

namespace hw {

template <Port P, std::uint8_t N>
class Pin {
    static_assert(N < 16, "у порту STM32 рівно 16 виводів");

public:
    static constexpr Port port = P;
    static constexpr std::uint32_t mask = 1u << N;

    // Напрямок пишемо ОСТАННІМ: каскад вмикається вже з готовими типом,
    // швидкістю й підтяжкою.
    [[nodiscard]] static std::expected<void, PinFault> configure(const PinConfig& cfg) noexcept
    {
        enableClock(P);
        GpioBlock& r = gpio(P);

        writeField2(r.pupdr, cfg.pull);
        writeField2(r.ospeedr, cfg.speed);
        writeBit(r.otyper, cfg.type == OutputType::OpenDrain);
        writeField2(r.moder, cfg.mode);

        // Читання назад: під замком LCKR запис губиться мовчки.
        if (readField2(r.moder) != static_cast<std::uint32_t>(cfg.mode)) {
            return std::unexpected(PinFault::ConfigLocked);
        }
        return {};
    }

    static void high() noexcept { gpio(P).bsrr = mask; }
    static void low() noexcept { gpio(P).bsrr = mask << 16; }
    static void write(bool level) noexcept { level ? high() : low(); }

    // Що справді на ніжці.
    [[nodiscard]] static bool read() noexcept { return (gpio(P).idr & mask) != 0u; }

    // Що ми замовили. Розбіжність із read() — зовнішня проблема, не програмна.
    [[nodiscard]] static bool latched() noexcept { return (gpio(P).odr & mask) != 0u; }

private:
    static constexpr std::uint32_t kShift2 = static_cast<std::uint32_t>(N) * 2u;

    template <class E>
        requires std::is_enum_v<E>
    static void writeField2(volatile std::uint32_t& reg, E value) noexcept
    {
        std::uint32_t v = reg;
        v &= ~(3u << kShift2);
        v |= (static_cast<std::uint32_t>(value) & 3u) << kShift2;
        reg = v;
    }

    [[nodiscard]] static std::uint32_t readField2(const volatile std::uint32_t& reg) noexcept
    {
        return (reg >> kShift2) & 3u;
    }

    static void writeBit(volatile std::uint32_t& reg, bool set) noexcept
    {
        if (set) {
            reg |= mask;
        } else {
            reg &= ~mask;
        }
    }
};

} // namespace hw
