// mcu.hpp — регістрова мапа GPIO і базові типи конфігурації.
// Ті самі адреси й поля, що в C-версії (STM32F4, RM0090), але описані так,
// щоб більшість помилок ловилася ще на етапі компіляції.
#pragma once

#include <cstdint>
#include <string_view>

namespace hw {

// Блок регістрів одного порту; порядок полів = порядок зсувів.
struct GpioBlock {
    volatile std::uint32_t moder;   // 0x00 режим виводу
    volatile std::uint32_t otyper;  // 0x04 push-pull / open-drain
    volatile std::uint32_t ospeedr; // 0x08 швидкість наростання фронту
    volatile std::uint32_t pupdr;   // 0x0C внутрішні підтяжки
    volatile std::uint32_t idr;     // 0x10 реальний рівень на ніжці
    volatile std::uint32_t odr;     // 0x14 засувка вихідного рівня
    volatile std::uint32_t bsrr;    // 0x18 атомарні set / reset
    volatile std::uint32_t lckr;    // 0x1C замок конфігурації
    volatile std::uint32_t afr[2];  // 0x20 альтернативні функції
};

enum class Port : std::uint32_t { A = 0, B = 1, C = 2, D = 3, E = 4 };

enum class Mode : std::uint32_t { Input = 0, Output = 1, Alternate = 2, Analog = 3 };
enum class OutputType : std::uint32_t { PushPull = 0, OpenDrain = 1 };
enum class Speed : std::uint32_t { Low = 0, Medium = 1, High = 2, VeryHigh = 3 };
enum class Pull : std::uint32_t { None = 0, Up = 1, Down = 2 };

struct PinConfig {
    Mode mode{Mode::Input};
    OutputType type{OutputType::PushPull};
    Speed speed{Speed::Low};
    Pull pull{Pull::None};
};

// Єдина помилка, яку взагалі може повернути конфігурація виводу: усе інше
// (номер піна, існування порту) відсіяно шаблонними параметрами.
enum class PinFault : std::uint8_t { ConfigLocked };

[[nodiscard]] constexpr std::string_view describe(PinFault f) noexcept
{
    switch (f) {
    case PinFault::ConfigLocked: return "конфігурацію порту замкнено (LCKR)";
    }
    return "невідома помилка";
}

inline constexpr std::uintptr_t kAhb1PeriphBase = 0x4002'0000u;
inline constexpr std::uintptr_t kGpioPortStride = 0x400u;
inline constexpr std::uintptr_t kRccBase        = 0x4002'3800u;
inline constexpr std::uintptr_t kRccAhb1EnrOff  = 0x30u;

[[nodiscard]] inline GpioBlock& gpio(Port p) noexcept
{
    const auto address = kAhb1PeriphBase + kGpioPortStride * static_cast<std::uintptr_t>(p);
    return *reinterpret_cast<GpioBlock*>(address);
}

inline void enableClock(Port p) noexcept
{
    auto& enr = *reinterpret_cast<volatile std::uint32_t*>(kRccBase + kRccAhb1EnrOff);
    enr |= 1u << static_cast<std::uint32_t>(p);

    // Тактування вмикається із затримкою в кілька тактів — читаємо назад.
    [[maybe_unused]] const std::uint32_t sync = enr;
}

// Груба затримка на порожньому циклі: приклад не потребує налаштованого SysTick.
inline void spin(std::uint32_t loops) noexcept
{
    for (volatile std::uint32_t i = 0; i < loops; ++i) {
    }
}

} // namespace hw
