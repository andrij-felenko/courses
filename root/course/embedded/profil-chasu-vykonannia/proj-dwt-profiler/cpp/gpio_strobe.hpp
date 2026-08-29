// gpio_strobe.hpp — стробування виводу для осцилографа через BSRR (STM32F4/F7).
//
// Запис у BSRR атомарний і коштує 1-2 такти AHB: біти 0..15 ставлять рівень
// у одиницю, біти 16..31 — у нуль. Ні читання-модифікації-запису, ні глушіння
// переривань, на відміну від ODR ^= PIN.
#pragma once

#include <cstdint>

namespace embedded::profiler {

namespace gpio {

inline constexpr std::uintptr_t ahb1_gpio_base = 0x40020000U;
inline constexpr std::uintptr_t port_stride = 0x400U;
inline constexpr std::uintptr_t port_a = ahb1_gpio_base;
inline constexpr std::uintptr_t port_b = ahb1_gpio_base + port_stride;
inline constexpr std::uintptr_t port_c = ahb1_gpio_base + 2 * port_stride;

inline constexpr std::uintptr_t rcc_ahb1enr = 0x40023830U;

// Зсуви регістрів порту (RM0090, «General-purpose I/Os»)
inline constexpr std::uintptr_t moder = 0x00U;
inline constexpr std::uintptr_t otyper = 0x04U;
inline constexpr std::uintptr_t ospeedr = 0x08U;
inline constexpr std::uintptr_t pupdr = 0x0CU;
inline constexpr std::uintptr_t bsrr = 0x18U;

} // namespace gpio

/// Вивід стробування, заданий на етапі компіляції: адреса регістра й маска
/// біта згортаються в константи, тож у машинному коді лишається один store.
template <std::uintptr_t PortBase, std::uint8_t Pin>
struct StrobePin {
    static_assert(Pin < 16, "у порту STM32 лише виводи 0..15");
    static_assert(PortBase >= gpio::port_a && (PortBase - gpio::port_a) % gpio::port_stride == 0,
                  "PortBase має бути базою порту GPIO на шині AHB1");

    static constexpr std::uint32_t port_index =
        static_cast<std::uint32_t>((PortBase - gpio::ahb1_gpio_base) / gpio::port_stride);

    static volatile std::uint32_t& reg(std::uintptr_t offset) noexcept {
        return *reinterpret_cast<volatile std::uint32_t*>(PortBase + offset);
    }

    /// Вихід, push-pull, максимальна крутість фронту.
    static void configure() noexcept {
        auto& ahb1 = *reinterpret_cast<volatile std::uint32_t*>(gpio::rcc_ahb1enr);
        ahb1 |= (1U << port_index);
        // Тактування вмикається не миттєво: перший запис у регістр порту
        // одразу після RCC губиться. Читання-назад дає потрібну затримку.
        static_cast<void>(ahb1);

        constexpr std::uint32_t pin2 = static_cast<std::uint32_t>(Pin) * 2U;

        reg(gpio::moder) = (reg(gpio::moder) & ~(3U << pin2)) | (1U << pin2); // 01 — вихід
        reg(gpio::otyper) &= ~(1U << Pin);                                    // push-pull
        // 11 — Very High Speed: найкрутіший фронт, який дає каскад. Із щупом
        // на 10-15 пФ навіть він розтягує наростання на десяток наносекунд.
        reg(gpio::ospeedr) |= (3U << pin2);
        reg(gpio::pupdr) &= ~(3U << pin2); // без підтяжок

        set_low();
    }

    static void set_high() noexcept { reg(gpio::bsrr) = 1U << Pin; }
    static void set_low() noexcept { reg(gpio::bsrr) = 1U << (Pin + 16U); }
};

/// RAII-строб: імпульс точно збігається з областю видимості об'єкта,
/// хай навіть з неї виходять раннім return.
template <typename Pin>
class ScopedStrobe {
public:
    ScopedStrobe() noexcept { Pin::set_high(); }
    ~ScopedStrobe() noexcept { Pin::set_low(); }

    ScopedStrobe(const ScopedStrobe&) = delete;
    ScopedStrobe& operator=(const ScopedStrobe&) = delete;
    ScopedStrobe(ScopedStrobe&&) = delete;
    ScopedStrobe& operator=(ScopedStrobe&&) = delete;
};

} // namespace embedded::profiler
