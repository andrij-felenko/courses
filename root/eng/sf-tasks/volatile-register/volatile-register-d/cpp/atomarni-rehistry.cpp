#include <cstdint>

struct GPIO_TypeDef {
    volatile std::uint32_t MODER;
    volatile std::uint32_t OTYPER;
    volatile std::uint32_t OSPEEDR;
    volatile std::uint32_t PUPDR;
    const volatile std::uint32_t IDR;
    volatile std::uint32_t ODR;
    volatile std::uint32_t BSRR;
};

inline constexpr std::uintptr_t GPIOA_BASE = 0x40020000UL;

inline GPIO_TypeDef& get_gpioa() noexcept {
    return *reinterpret_cast<GPIO_TypeDef*>(GPIOA_BASE);
}

class GPIOPin {
public:
    constexpr explicit GPIOPin(std::uint8_t pin_idx) noexcept : pin_mask_{1U << pin_idx} {}

    void set_high(GPIO_TypeDef &gpio) const noexcept {
        gpio.BSRR = pin_mask_; // Атомарний запис встановлення
    }

    void set_low(GPIO_TypeDef &gpio) const noexcept {
        gpio.BSRR = (pin_mask_ << 16); // Атомарний запис скидання
    }

private:
    std::uint32_t pin_mask_;
};
