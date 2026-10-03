#include "tim1_pwm.hpp"
#include "adc_opamp.hpp"
#include "foc_controller.hpp"

// Глобальні об'єкти FOC-системи
static foc::Tim1PwmDriver g_pwm_driver(20000, 1000); // 20 кГц ШІМ, 1 мкс dead-time
static foc::AdcOpampDriver g_adc_driver(0.005f);     // Масштаб 5мА на LSB
static foc::FOCController g_foc_controller(g_pwm_driver, g_adc_driver);

/**
 * @brief Обробник переривання завершення інжектованого перетворення АЦП (ADC1_2_IRQHandler).
 * Викликається синхронно на кожному періоді ШІМ для виконання векторного керування у реальному часі.
 */
extern "C" void ADC1_2_IRQHandler(void) {
#ifdef ADC1
    if (ADC1->ISR & ADC_ISR_JEOC) {
        ADC1->ISR |= ADC_ISR_JEOC; // Очищення прапорця переривання JEOC

        // Викликаємо обчислювальний цикл FOC
        g_foc_controller.updateInterruptHandler();
    }
#else
    g_foc_controller.updateInterruptHandler();
#endif
}

/**
 * @brief Системне налаштування тактування STM32G431 до 170 МГц.
 */
static void SystemClock_Config(void) {
#ifdef RCC
    // Налаштування Flash Latency для 170 МГц
    FLASH->ACR &= ~FLASH_ACR_LATENCY;
    FLASH->ACR |= FLASH_ACR_LATENCY_4WS;

    // Увімкнення HSI (16 МГц)
    RCC->CR |= RCC_CR_HSION;
    while (!(RCC->CR & RCC_CR_HSIRDY)) {}

    // Конфігурація PLL: HSI (16 МГц) / M=4 * N=85 / R=2 = 170 МГц
    RCC->PLLCFGR = RCC_PLLCFGR_PLLSRC_HSI |
                   (3u << RCC_PLLCFGR_PLLM_Pos) |
                   (85u << RCC_PLLCFGR_PLLN_Pos) |
                   RCC_PLLCFGR_PLLREN;

    RCC->CR |= RCC_CR_PLLON;
    while (!(RCC->CR & RCC_CR_PLLRDY)) {}

    // Вибір PLL як джерела системного тактування
    RCC->CFGR |= RCC_CFGR_SW_PLL;
    while ((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_PLL) {}
#endif
}

int main(void) {
    // 1. Конфігурація системного тактового генератора
    SystemClock_Config();

    // 2. Ініціалізація підсистем FOC-контролера
    if (!g_foc_controller.init()) {
        while (true) {
            // Помилка ініціалізації периферії
        }
    }

    // 3. Запуск FOC-контролера (автокалібрування та включення ШІМ)
    g_foc_controller.start();

    // 4. Встановлення початкового значення струму моменту Iq = 1.0A, Id = 0.0A
    g_foc_controller.setTargetCurrents(0.0f, 1.0f);

    float mock_angle = 0.0f;

    // 5. Головний фоновий цикл програми
    while (true) {
        // Симуляція оновлення електричного кута ротора (Open-loop обертання для демонстрації)
        mock_angle += 0.001f;
        if (mock_angle > 3.14159265f) {
            mock_angle -= 2.0f * 3.14159265f;
        }
        g_foc_controller.setElectricalAngle(mock_angle);

        // Проста затримка фонового циклу
        for (volatile int i = 0; i < 10000; ++i) {
            __NOP();
        }
    }

    return 0;
}
