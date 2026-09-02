#pragma once

#include "mmio.hpp"

namespace board {

// Вивід порту як ТИП: і порт, і номер відомі на етапі компіляції, тому маски
// рахує компілятор, а не процесор.
template <std::uintptr_t PortBase, unsigned PinNo>
class Pin {
    static_assert(PinNo < 16u, "у порту STM32F1 шістнадцять виводів");

    // Виводи 0..7 конфігурує CRL, 8..15 — CRH; вибір робить сам тип.
    using Cfg = mmio::Reg<PortBase + (PinNo < 8u ? 0x00u : 0x04u)>;
    using Idr = mmio::Reg<PortBase + 0x08u>;
    using Odr = mmio::Reg<PortBase + 0x0Cu>;
    using Bsrr = mmio::Reg<PortBase + 0x10u>;
    using Brr = mmio::Reg<PortBase + 0x14u>;

    static constexpr unsigned kShift = (PinNo % 8u) * 4u;
    static constexpr std::uint32_t kCfgMask = 0xFu << kShift;

public:
    static constexpr std::uint32_t kBit = 1u << PinNo;

    static void configureInputPullUp() noexcept {
        Cfg::modify(kCfgMask, 0x8u << kShift);  // CNF=10 (вхід із підтяжкою), MODE=00
        Odr::setBits(kBit);                     // одиниця в ODR = підтяжка вгору
    }

    // Вихід push-pull, 2 МГц: крутіші фронти індикації не потрібні, а зайва
    // швидкість — це лише завади на сусідніх доріжках плати.
    static void configureOutputPushPull() noexcept {
        Cfg::modify(kCfgMask, 0x2u << kShift);  // CNF=00, MODE=10
    }

    // Схема Active-LOW дозволяє й відкритий стік (CNF=01): у логічній одиниці
    // вивід іде в Hi-Z, і світлодіод можна живити від 5 В на 5V-толерантній
    // ніжці, не подаючи цих 5 В на шину 3.3 В ядра.
    static void configureOutputOpenDrain() noexcept {
        Cfg::modify(kCfgMask, 0x6u << kShift);  // CNF=01, MODE=10
    }

    [[nodiscard]] static bool level() noexcept { return (Idr::read() & kBit) != 0u; }

    // BSRR/BRR перемикають один біт без читання ODR, тож обробник переривання
    // не може затерти сусідній вивід того самого порту.
    static void high() noexcept { Bsrr::write(kBit); }
    static void low() noexcept { Brr::write(kBit); }
    [[nodiscard]] static bool latched() noexcept { return (Odr::read() & kBit) != 0u; }
};

// PC13: анод на 3.3 В, катод через баластні 330 Ом до ніжки — активний нуль.
struct Led {
    using PinT = Pin<soc::kGpioC, 13>;

    static void init() noexcept {
        mmio::Reg<soc::kRccApb2Enr>::setBits(soc::kIopcEn);
        PinT::configureOutputPushPull();
        set(false);
    }
    static void set(bool on) noexcept { on ? PinT::low() : PinT::high(); }
    [[nodiscard]] static bool isOn() noexcept { return !PinT::latched(); }
    static void toggle() noexcept { set(!isOn()); }
};

// PA0: кнопка на землю, зовнішні R1=10 кОм і C=100 нФ. Внутрішню підтяжку
// вмикаємо теж — вона рятує вхід від наведень, поки плату не допаяли.
struct Button {
    using PinT = Pin<soc::kGpioA, 0>;

    static void init() noexcept {
        mmio::Reg<soc::kRccApb2Enr>::setBits(soc::kIopaEn | soc::kAfioEn);
        PinT::configureInputPullUp();
    }
    [[nodiscard]] static bool isPressed() noexcept { return !PinT::level(); }
};

}  // namespace board
