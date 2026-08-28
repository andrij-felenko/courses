#include "stm32f4xx_hal.h"

#define DO_PORT  GPIOA
#define DO_PIN   GPIO_PIN_0        // PA0 у CubeMX: GPIO_EXTI0, тригер — RISING

volatile uint32_t sound_count    = 0;
volatile uint32_t last_event_isr = 0;
#define WINDOW_MS  300

// Обробник фронту: HAL кличе його з EXTI0_IRQHandler. Якнайкоротший —
// лише рахуємо подію з тим самим вікном придушення.
void HAL_GPIO_EXTI_Callback(uint16_t pin) {
    if (pin != DO_PIN) return;                  // на цей колбек сходяться всі лінії EXTI
    uint32_t now = HAL_GetTick();               // тики йде лічити SysTick, читати можна
    if (now - last_event_isr > WINDOW_MS) {
        last_event_isr = now;
        sound_count++;
    }
}

int main(void) {
    /* HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); — генерує CubeMX;
       він же вмикає лінію: HAL_NVIC_SetPriority(EXTI0_IRQn, 2, 0);
                            HAL_NVIC_EnableIRQ(EXTI0_IRQn);           */
    HAL_Delay(300);
    uint32_t shown = 0;
    while (1) {
        uint32_t c = sound_count;   // на 32-бітному ядрі це читання одною командою
        if (c != shown) {           // друкуємо лише коли лічильник змінився
            shown = c;
            printf("подій: %lu\r\n", (unsigned long)c);
        }
        // while(1) майже вільний — уся реакція на звук живе в перериванні
    }
}
