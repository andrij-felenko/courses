#ifndef STM32_GPIO_EXTI_HPP
#define STM32_GPIO_EXTI_HPP

#include <cstdint>
#include "ss41f_hall_decoder.hpp"

namespace stm32 {

/**
 * @brief Імітація регістрів GPIO STM32 для демонстрації низькорівневого RAII-драйвера.
 */
struct GpioRegisterMap {
    volatile uint32_t MODER;   // Регістр режиму роботи пінів
    volatile uint32_t PUPDR;   // Регістр підтягуючих резисторів (Pull-up/Pull-down)
    volatile uint32_t IDR;     // Регістр вхідних даних пінів
    volatile uint32_t ODR;     // Регістр вихідних даних пінів
};

/**
 * @brief Імітація регістрів EXTI STM32 (External Interrupt Controller).
 */
struct ExtiRegisterMap {
    volatile uint32_t IMR;    // Interrupt Mask Register (Маска переривань)
    volatile uint32_t RTSR;   // Rising Trigger Selection Register (Фронт)
    volatile uint32_t FTSR;   // Falling Trigger Selection Register (Зпад)
    volatile uint32_t PR;     // Pending Register (Прапорець очікування)
};

/**
 * @brief Структура конфігурації піна GPIO для датчиків SS41F.
 */
struct GpioPinConfig {
    GpioRegisterMap* port;
    uint8_t pin_index; // 0..15
};

/**
 * @brief RAII-модуль конфігурації та управління 3-ма вхідними лініями GPIO/EXTI мікроконтролера STM32.
 * 
 * Клас автоматично ініціалізує три вхідні лінії для сигналів Hall A, Hall B, Hall C від датчиків SS41F,
 * налаштовує переривання EXTI за обома фронтами (Rising/Falling) та вимикає периферію в деструкторі.
 */
class GpioExtiGuard {
public:
    GpioExtiGuard(bldc::Ss41fHallDecoder& decoder,
                  GpioPinConfig pin_a,
                  GpioPinConfig pin_b,
                  GpioPinConfig pin_c) noexcept;
    ~GpioExtiGuard();

    GpioExtiGuard(const GpioExtiGuard&) = delete;
    GpioExtiGuard& operator=(const GpioExtiGuard&) = delete;
    GpioExtiGuard(GpioExtiGuard&&) = delete;
    GpioExtiGuard& operator=(GpioExtiGuard&&) = delete;

    /**
     * @brief Атомарне зчитування поточного 3-бітного стану пінів (Hall A | Hall B | Hall C).
     */
    [[nodiscard]] uint8_t read_raw_pins() const noexcept;

    /**
     * @brief Апаратний обробник переривань EXTI ISR (викликається при зміні будь-якого з пінів).
     * @param timestamp_us Часова мітка апаратного таймера у мікросекундах.
     */
    void handle_isr(uint32_t timestamp_us) noexcept;

    /**
     * @brief Ручна імітація зміни логічних рівнів на вхідних пінах для тестування без заліза.
     */
    void simulate_pin_change(uint8_t raw_3bit_code, uint32_t timestamp_us) noexcept;

private:
    void init_hardware() noexcept;
    void deinit_hardware() noexcept;

    bldc::Ss41fHallDecoder& decoder_;
    GpioPinConfig pin_a_;
    GpioPinConfig pin_b_;
    GpioPinConfig pin_c_;

    ExtiRegisterMap exti_regs_{0, 0, 0, 0};
    bool hardware_initialized_{false};
};

} // namespace stm32

#endif // STM32_GPIO_EXTI_HPP
