#ifndef STM32_EXTI_GUARD_HPP
#define STM32_EXTI_GUARD_HPP

#include <cstdint>
#include <functional>

namespace stm32 {

// Структура конфігурації пина GPIO та лінії EXTI для STM32
struct ExtiConfig {
    void* gpio_port{nullptr};   // Вказівник на периферийний порт GPIO (напр., GPIOA)
    uint16_t gpio_pin{0};       // Пін GPIO (напр., GPIO_PIN_0)
    uint32_t exti_line{0};      // Лінія EXTI (напр., EXTI_LINE_0)
    int irq_number{0};          // Номер векторного переривання NVIC (IRQn_Type)
};

// RAII-клас управління апаратним перериванням STM32 EXTI
class ExtiInterruptGuard {
public:
    using IsrCallback = std::function<void()>;

    explicit ExtiInterruptGuard(const ExtiConfig& config);
    ~ExtiInterruptGuard();

    ExtiInterruptGuard(const ExtiInterruptGuard&) = delete;
    ExtiInterruptGuard& operator=(const ExtiInterruptGuard&) = delete;

    // Реєстрація callback-функції, яка буде викликана при спрацьовуванні EXTI
    void register_callback(IsrCallback cb);

    // Увімкнути обробку переривань у NVIC
    void enable_interrupt();

    // Вимкнути обробку переривань у NVIC
    void disable_interrupt();

    // Обробник переривання, який закликується з низькорівневого ISR
    void handle_isr();

    static ExtiInterruptGuard* instance; // Вказівник для зв'язку з низькорівневим вектором C

private:
    ExtiConfig config_;
    IsrCallback callback_{nullptr};
    bool is_enabled_{false};

    void configure_hardware();
};

} // namespace stm32

#endif // STM32_EXTI_GUARD_HPP
