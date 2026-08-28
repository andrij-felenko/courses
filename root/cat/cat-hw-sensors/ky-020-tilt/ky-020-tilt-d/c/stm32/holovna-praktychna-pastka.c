#include "main.h"          // CubeMX: PA0 — GPIO_Input без підтяжки (10 кОм на модулі)

#define TILT_PORT GPIOA
#define TILT_PIN  GPIO_PIN_0
#define SETTLE    30u              // мс: скільки рівень має протриматися

void tilt_count(void) {            // викликати з main() після MX_GPIO_Init()
    GPIO_PinState stable  = GPIO_PIN_SET;   // усталений стан (SET = рівно)
    GPIO_PinState lastRaw = GPIO_PIN_SET;   // попереднє СИРЕ читання
    uint32_t lastChange = HAL_GetTick();    // коли сире читання востаннє смикнулось
    uint32_t tilts = 0;                     // лічильник справжніх нахилів

    while (1) {
        GPIO_PinState raw = HAL_GPIO_ReadPin(TILT_PORT, TILT_PIN);  // сире, брязкуче
        if (raw != lastRaw) {                   // рівень щойно смикнувся —
            lastChange = HAL_GetTick();         // перезапускаємо відлік «тиші»
            lastRaw = raw;
        }
        // рівень протримався сталим довше за SETTLE → приймаємо його
        if (HAL_GetTick() - lastChange > SETTLE && raw != stable) {
            stable = raw;
            if (stable == GPIO_PIN_RESET) {     // перейшли саме в «нахил»
                tilts++;
                printf("нахилів: %lu\r\n", (unsigned long)tilts);
            }
        }
    }
}
