#include "stm32f4xx_hal.h"

volatile uint32_t pulses = 0;          // спільний лічильник — тому volatile

// HAL кличе цей callback з обробника EXTI — спільний на всі лінії
void HAL_GPIO_EXTI_Callback(uint16_t pin) {
    if (pin == SENSOR_Pin) pulses++;   // лише рахуємо — і все
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();                    // піна SENSOR: GPIO_MODE_IT_FALLING + GPIO_PULLUP
    HAL_NVIC_SetPriority(EXTI0_IRQn, 5, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);    // дозволити переривання лінії

    uint32_t last = 0;
    while (1) {
        if (HAL_GetTick() - last >= 1000) {   // раз на секунду
            last = HAL_GetTick();
            __disable_irq();                  // безпечно зняти спільне значення
            uint32_t n = pulses; pulses = 0;
            __enable_irq();
            printf("%lu\r\n", (unsigned long)n);  // друк — у main, НЕ в обробнику
        }
    }
}
