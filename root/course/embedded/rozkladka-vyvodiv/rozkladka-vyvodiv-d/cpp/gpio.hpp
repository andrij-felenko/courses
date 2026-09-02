#pragma once

// Опис розкладки виводів STM32F4 у типах. Той самий предмет, що й у C,
// але помилка тут — значення (std::expected), а не код повернення.
// Потрібен C++23: std::expected.

#include "stm32f4xx.h"

#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

namespace mcu::gpio {

// Межі з технічного опису родини.
struct Limits {
    static constexpr unsigned pin_ma    = 20;   // одна звичайна ніжка
    static constexpr unsigned backup_ma = 3;    // PC13..PC15
    static constexpr unsigned port_ma   = 80;   // сума по порту
    static constexpr unsigned chip_ma   = 150;  // сума по кристалу
};

enum class Mode : std::uint32_t { Input = 0, Output = 1, Alternate = 2, Analog = 3 };

// Крутизна фронту, а не частота сигналу.
enum class Speed : std::uint32_t {
    Low      = 0,  // t_rise ~25-30 нс
    Medium   = 1,  // t_rise ~10-12 нс
    High     = 2,  // t_rise ~4-6 нс
    VeryHigh = 3   // t_rise ~1.5 нс, спектр до ~233 МГц
};

enum class Pull  : std::uint32_t { None = 0, Up = 1, Down = 2 };
enum class Drive : std::uint32_t { PushPull = 0, OpenDrain = 1 };

// Електричний клас із таблиці виводів технічного опису.
enum class ElectricalClass : std::uint8_t {
    Tt,      // стандартний цифровий, межа VDD + 0.3 В
    Ft,      // витримує 5.5 В, немає діода на VDD
    Tta,     // заведений на мультиплексор АЦП/ЦАП
    Backup,  // PC13..PC15, домен резервного живлення
    System   // PA13/PA14, шина налагодження SWD
};

struct Pin {
    GPIO_TypeDef* port;
    std::uint8_t  number;

    friend bool operator==(const Pin&, const Pin&) noexcept = default;
};

// Один рядок таблиці розпіновки плати.
struct PinPlan {
    std::string_view signal;
    Pin              pin;
    Mode             mode;
    std::uint8_t     af      = 0;                     // значуще лише для Alternate
    Speed            speed   = Speed::Low;
    Pull             pull    = Pull::None;
    Drive            drive   = Drive::PushPull;
    ElectricalClass  ec      = ElectricalClass::Tt;
    unsigned         load_ma = 0;                     // оголошений струм навантаження
};

enum class Reason : std::uint8_t {
    UnknownPort,
    PinOutOfRange,
    DebugPin,          // спроба забрати PA13/PA14 у SWD
    ClassMismatch,     // клас суперечить самій ніжці
    AnalogOnDigital,
    AfOutOfRange,
    AfUnused,
    SlewTooFast,
    BackupAlternate,
    BackupSpeed,
    BackupCurrent,
    PinCurrent,
    PortCurrent,
    ChipCurrent,
    Duplicate,         // дві функції на одній ніжці
    LockFailed
};

struct Fault {
    Reason           reason;
    std::string_view signal;         // назва ланцюга зі схеми
    std::string_view rival{};        // другий претендент на ніжку
    unsigned         value = 0;      // що просили
    unsigned         limit = 0;      // що дозволено
};

[[nodiscard]] std::string_view describe(Reason reason) noexcept;

// Звіряє ВСЮ таблицю з межами й лише потім чіпає регістри.
[[nodiscard]] std::expected<void, Fault> apply(std::span<const PinPlan> layout) noexcept;

// Звільняє JTDI (PA15), JTDO/SWO (PB3), NJTRST (PB4) під звичайний GPIO
// і замикає PA13/PA14 апаратним замком LCKR до наступного скидання.
[[nodiscard]] std::expected<void, Fault> secure_debug_port() noexcept;

[[nodiscard]] unsigned port_budget_ma(const GPIO_TypeDef* port) noexcept;
[[nodiscard]] unsigned chip_budget_ma() noexcept;

}  // namespace mcu::gpio
