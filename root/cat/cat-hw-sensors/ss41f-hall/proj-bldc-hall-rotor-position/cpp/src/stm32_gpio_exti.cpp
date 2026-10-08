#include "stm32_gpio_exti.hpp"

namespace stm32 {

GpioExtiGuard::GpioExtiGuard(bldc::Ss41fHallDecoder& decoder,
                             GpioPinConfig pin_a,
                             GpioPinConfig pin_b,
                             GpioPinConfig pin_c) noexcept
    : decoder_(decoder), pin_a_(pin_a), pin_b_(pin_b), pin_c_(pin_c) {
    init_hardware();
}

GpioExtiGuard::~GpioExtiGuard() {
    deinit_hardware();
}

void GpioExtiGuard::init_hardware() noexcept {
    // 1. Конфігурація режимів вхідних пінів GPIO (MODE_INPUT = 00b, PUPDR_PULLUP = 01b)
    if (pin_a_.port) {
        pin_a_.port->MODER &= ~(0x03U << (pin_a_.pin_index * 2));
        pin_a_.port->PUPDR |= (0x01U << (pin_a_.pin_index * 2));
    }
    if (pin_b_.port) {
        pin_b_.port->MODER &= ~(0x03U << (pin_b_.pin_index * 2));
        pin_b_.port->PUPDR |= (0x01U << (pin_b_.pin_index * 2));
    }
    if (pin_c_.port) {
        pin_c_.port->MODER &= ~(0x03U << (pin_c_.pin_index * 2));
        pin_c_.port->PUPDR |= (0x01U << (pin_c_.pin_index * 2));
    }

    // 2. Налаштування лінії зовнішніх переривань EXTI за обома фронтами (Rising і Falling)
    const uint32_t mask_a = (1U << pin_a_.pin_index);
    const uint32_t mask_b = (1U << pin_b_.pin_index);
    const uint32_t mask_c = (1U << pin_c_.pin_index);
    const uint32_t total_mask = mask_a | mask_b | mask_c;

    exti_regs_.IMR |= total_mask;   // Розблокування лінії переривання
    exti_regs_.RTSR |= total_mask;  // Тригер за зростаючим фронтом
    exti_regs_.FTSR |= total_mask;  // Тригер за спадаючим фронтом

    hardware_initialized_ = true;
}

void GpioExtiGuard::deinit_hardware() noexcept {
    if (!hardware_initialized_) {
        return;
    }

    const uint32_t mask_a = (1U << pin_a_.pin_index);
    const uint32_t mask_b = (1U << pin_b_.pin_index);
    const uint32_t mask_c = (1U << pin_c_.pin_index);
    const uint32_t total_mask = mask_a | mask_b | mask_c;

    // Скидання маски переривань EXTI
    exti_regs_.IMR &= ~total_mask;
    exti_regs_.RTSR &= ~total_mask;
    exti_regs_.FTSR &= ~total_mask;

    hardware_initialized_ = false;
}

uint8_t GpioExtiGuard::read_raw_pins() const noexcept {
    uint8_t val_a = 0;
    uint8_t val_b = 0;
    uint8_t val_c = 0;

    if (pin_a_.port) {
        val_a = (pin_a_.port->IDR >> pin_a_.pin_index) & 0x01U;
    }
    if (pin_b_.port) {
        val_b = (pin_b_.port->IDR >> pin_b_.pin_index) & 0x01U;
    }
    if (pin_c_.port) {
        val_c = (pin_c_.port->IDR >> pin_c_.pin_index) & 0x01U;
    }

    return static_cast<uint8_t>((val_a << 2) | (val_b << 1) | val_c);
}

void GpioExtiGuard::handle_isr(uint32_t timestamp_us) noexcept {
    // 1. Атомарно зчитуємо поточний стан усіх трьох фазових пінів
    const uint8_t raw_code = read_raw_pins();

    // 2. Скидаємо прапорці очікування EXTI PR
    exti_regs_.PR |= (1U << pin_a_.pin_index) | (1U << pin_b_.pin_index) | (1U << pin_c_.pin_index);

    // 3. Передаємо 3-бітну комбінацію в C++ драйвер-декодер
    decoder_.process_hall_change(raw_code, timestamp_us);
}

void GpioExtiGuard::simulate_pin_change(uint8_t raw_3bit_code, uint32_t timestamp_us) noexcept {
    const uint8_t val_a = (raw_3bit_code >> 2) & 0x01U;
    const uint8_t val_b = (raw_3bit_code >> 1) & 0x01U;
    const uint8_t val_c = raw_3bit_code & 0x01U;

    if (pin_a_.port) {
        pin_a_.port->IDR = (pin_a_.port->IDR & ~(1U << pin_a_.pin_index)) | (val_a << pin_a_.pin_index);
    }
    if (pin_b_.port) {
        pin_b_.port->IDR = (pin_b_.port->IDR & ~(1U << pin_b_.pin_index)) | (val_b << pin_b_.pin_index);
    }
    if (pin_c_.port) {
        pin_c_.port->IDR = (pin_c_.port->IDR & ~(1U << pin_c_.pin_index)) | (val_c << pin_c_.pin_index);
    }

    // Симуляція спрацьовування апаратного переривання EXTI ISR
    handle_isr(timestamp_us);
}

} // namespace stm32
