#include "stm32_timer_hal.hpp"
#include "encoder.hpp"
#include <iostream>
#include <iomanip>

// Симуляція периферійного таймера TIM2 в апаратній пам'яті STM32
static TIM_RegisterMap SimulatedTIM2_Regs{};

// Глобальні об'єкти для обробки апаратних переривань
static Stm32Timer stm32_timer(&SimulatedTIM2_Regs);
static EncoderConfig config{
    .pulses_per_revolution = 1024,      // 1024 PPR (4096 тиків/оберт при x4)
    .x4_encoding = true,
    .filter_icf = 6,                    // Апаратний фільтр завад
    .speed_update_interval_sec = 0.01f, // 10 мс квант часу
    .invert_direction = false
};
static QuadratureEncoder encoder(stm32_timer, config);

/**
 * @brief Обробник векторного переривання оновлення таймера TIM2 (TIM2_IRQHandler).
 * Реальний вектор STM32 викликає цей метод при підповненні або переповненні TIMx->CNT.
 */
extern "C" void TIM2_IRQHandler() {
    if (stm32_timer.getAndClearUpdateFlag()) {
        encoder.handleTimerOverflowISR();
    }
}

/**
 * @brief Обробник зовнішнього переривання індексного сигналу Z (EXTI0_IRQHandler).
 */
extern "C" void EXTI0_IRQHandler() {
    encoder.handleIndexPulseISR();
}

int main() {
    std::cout << "========================================================\n";
    std::cout << "   C++ Драйвер Квадратурного Енкодера для STM32 (x4)   \n";
    std::cout << "========================================================\n\n";

    // Ініціалізація драйвера та апаратури
    encoder.init();

    std::cout << "[ІНІЦІАЛІЗАЦІЯ] Роздільна здатність: " << config.pulses_per_revolution 
              << " PPR -> " << encoder.getCountsPerRev() << " відліків/оберт (x4 декодування).\n";
    std::cout << "[ІНІЦІАЛІЗАЦІЯ] Початковий стан калібрування Z-мітки: " 
              << (encoder.isCalibrated() ? "ТАК" : "НІ") << "\n\n";

    // 1. Симуляція прямого обертання з переповненням 16-бітного таймера
    std::cout << "--- КРОК 1: Симуляція прямого обертання та переповнення (Overflow) ---\n";
    constexpr float dt = 0.01f; // 10 мс
    
    // Імітуємо 70,000 відліків (перевищує 65,535 — відбувається overflow)
    SimulatedTIM2_Regs.CNT = 65530;
    encoder.update(dt);
    
    // Моделюємо перехід 65535 -> 0 та спрацьовування ISR
    SimulatedTIM2_Regs.CNT = 5;
    SimulatedTIM2_Regs.SR |= Stm32TimerRegs::SR_UIF; // Встановлюємо прапорець переповнення
    TIM2_IRQHandler(); // Виклик ISR переривання
    
    encoder.update(dt);
    EncoderState state = encoder.getState();

    std::cout << "Позиція відліків (32-біт): " << state.raw_position_counts << "\n";
    std::cout << "Кут повороту: " << std::fixed << std::setprecision(2) 
              << state.angle_degrees << " град (" << state.angle_radians << " рад)\n";
    std::cout << "Кутова швидкість: " << state.velocity_rad_per_sec << " рад/с (" 
              << state.velocity_rpm << " RPM)\n\n";

    // 2. Симуляція проходження індексної мітки Z (EXTI)
    std::cout << "--- КРОК 2: Прив'язка до нуля по індексній мітці Z (EXTI) ---\n";
    EXTI0_IRQHandler(); // Виклик переривання Z-мітки
    encoder.update(dt);
    state = encoder.getState();

    std::cout << "Калібрування завершено: " << (state.is_calibrated ? "ТАК" : "НІ") << "\n";
    std::cout << "Нульовий зсув позиції: " << state.zero_offset_counts << " відліків\n";
    std::cout << "Відносний кут після калібрування: " << state.angle_degrees << " град\n\n";

    // 3. Симуляція реверсивного руху (Underflow)
    std::cout << "--- КРОК 3: Симуляція реверсивного руху та підповнення (Underflow) ---\n";
    SimulatedTIM2_Regs.CR1 |= Stm32TimerRegs::CR1_DIR; // Встановлюємо напрямок Down
    SimulatedTIM2_Regs.CNT = 65500;
    SimulatedTIM2_Regs.SR |= Stm32TimerRegs::SR_UIF;
    TIM2_IRQHandler(); // Врахування підповнення (underflow)

    encoder.update(dt);
    state = encoder.getState();

    std::cout << "Позиція відліків після реверсу: " << state.raw_position_counts << "\n";
    std::cout << "Швидкість при реверсі: " << state.velocity_rpm << " RPM (" 
              << state.velocity_rad_per_sec << " рад/с)\n\n";

    std::cout << "========================================================\n";
    std::cout << "  Тестування C++ драйвера квадратурного енкодера успішно завершено!  \n";
    std::cout << "========================================================\n";

    return 0;
}
