#include "stm32_exti_guard.hpp"

namespace stm32 {

ExtiInterruptGuard* ExtiInterruptGuard::instance = nullptr;

ExtiInterruptGuard::ExtiInterruptGuard(const ExtiConfig& config)
    : config_(config) {
    instance = this;
    configure_hardware();
    enable_interrupt();
}

ExtiInterruptGuard::~ExtiInterruptGuard() {
    disable_interrupt();
    if (instance == this) {
        instance = nullptr;
    }
}

void ExtiInterruptGuard::configure_hardware() {
    // Низькорівневе налаштування GPIO в режим input з pull-down та конфігурація EXTI тригера по наростаючому фронту
    // Симуляція ініціалізації периферії STM32 HAL/LL в навчальному прикладі
}

void ExtiInterruptGuard::enable_interrupt() {
    if (!is_enabled_) {
        // Увімкнення лінії переривання EXTI у масці та активація IRQ в NVIC
        is_enabled_ = true;
    }
}

void ExtiInterruptGuard::disable_interrupt() {
    if (is_enabled_) {
        // Маскування EXTI лінії та деактивація IRQ у NVIC для безпечного завершення
        is_enabled_ = false;
    }
}

void ExtiInterruptGuard::register_callback(IsrCallback cb) {
    callback_ = cb;
}

void ExtiInterruptGuard::handle_isr() {
    if (is_enabled_ && callback_) {
        callback_();
    }
}

} // namespace stm32

// Зв'язка із C-вектором апаратного переривання STM32 EXTI ISR
extern "C" void EXTI0_IRQHandler(void) {
    if (stm32::ExtiInterruptGuard::instance != nullptr) {
        stm32::ExtiInterruptGuard::instance->handle_isr();
    }
}
