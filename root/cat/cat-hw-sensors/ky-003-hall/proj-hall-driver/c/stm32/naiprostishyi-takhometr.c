#include "main.h"

#define WINDOW_MS 250                  // вікно вимірювання

volatile uint32_t pulses = 0;          // лічильник, який чіпає ISR

/* нога описана в CubeMX: GPIO_EXTI, Pull-up, Falling edge —
   відкритий колектор → підтяжка обовʼязкова */
void HAL_GPIO_EXTI_Callback(uint16_t pin) {   // ISR: якнайкоротша
    if (pin == HALL_Pin) pulses++;
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();                    // тут же вмикається EXTI на нозі
    uint32_t windowStart = HAL_GetTick();

    while (1) {
        if (HAL_GetTick() - windowStart < WINDOW_MS) continue;
        windowStart += WINDOW_MS;

        __disable_irq();               // цілісне зчитування й обнулення
        uint32_t n = pulses;
        pulses = 0;
        __enable_irq();

        // n імпульсів за WINDOW_MS мілісекунд; магніт один → n обертів за вікно
        float rpm = (float)n * (60000.0f / WINDOW_MS);
        printf("RPM: %.0f\r\n", rpm);   // printf перенаправлено на UART
    }
}
