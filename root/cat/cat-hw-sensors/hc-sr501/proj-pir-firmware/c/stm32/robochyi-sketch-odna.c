#include "main.h"    // CubeMX: PIR_Pin — вхід NOPULL, LED_Pin — вихід push-pull
#include <stdio.h>   // printf перенаправлено в UART

#define WARMUP_MS   60000U   // прогрів
#define LOCKOUT_MS  3000U    // не приймати нову подію раніше, ніж мине стільки

static uint32_t counter;     // скільки подій нарахували

static void alarm_event(void) {
    counter++;
    printf("ТРИВОГА, подія #%lu\r\n", (unsigned long)counter);
    // тут: надіслати пакет, зробити кадр, увімкнути сирену на мить тощо
    HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_SET);
    HAL_Delay(100);          // коротке блимання — для наочності
    HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_RESET);
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_USART2_UART_Init();

    uint32_t t_boot = HAL_GetTick(), t_last_event = 0;
    GPIO_PinState pir_prev = HAL_GPIO_ReadPin(PIR_GPIO_Port, PIR_Pin);

    while (1) {
        HAL_Delay(20);                       // грубий дебаунс краю
        uint32_t now = HAL_GetTick();
        if (now - t_boot < WARMUP_MS) continue;          // гасіння прогріву

        GPIO_PinState pir = HAL_GPIO_ReadPin(PIR_GPIO_Port, PIR_Pin);
        // Виявлення переднього фронту: було 0, стало 1 — це нова поява руху.
        if (pir == GPIO_PIN_SET && pir_prev == GPIO_PIN_RESET &&
            now - t_last_event >= LOCKOUT_MS) {
            t_last_event = now;
            alarm_event();
        }
        pir_prev = pir;
    }
}
