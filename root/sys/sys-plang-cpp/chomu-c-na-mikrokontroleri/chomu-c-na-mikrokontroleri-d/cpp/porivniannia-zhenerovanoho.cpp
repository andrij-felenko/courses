// cpp_gpio_config.hpp
#include <cstdint>

enum class Pin : uint8_t { P5 = 5 };
enum class Mode : uint32_t { Input = 0b00, Output = 0b01 };

template <uintptr_t Base>
struct Gpio {
    template <Pin P, Mode M>
    static inline void set_mode() noexcept {
        constexpr uint32_t shift = static_cast<uint8_t>(P) * 2U;
        constexpr uint32_t clear_mask = 0b11U << shift;
        constexpr uint32_t set_mask = static_cast<uint32_t>(M) << shift;

        auto* reg = reinterpret_cast<volatile uint32_t*>(Base);
        *reg = (*reg & ~clear_mask) | set_mask;
    }
};

using GpioA = Gpio<0x40020000UL>;

void configure_pin_cpp() {
    GpioA::set_mode<Pin::P5, Mode::Output>();
}
