#include "main.h"   // CubeMX: PIR_Pin — GPIO_MODE_IT_RISING + PULLDOWN, NVIC на EXTI увімкнено

volatile uint8_t motion_flag = 0;   // ISR лише піднімає прапорець

void HAL_GPIO_EXTI_Callback(uint16_t pin) {   // це і є тіло ISR: коротко, без роботи
    if (pin == PIR_Pin) motion_flag = 1;
}

static void go_to_sleep(void) {
    HAL_SuspendTick();          // щоб SysTick не будив ядро щомілісекунди
    HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);   // ← ядро засинає тут

    // --- Прокинулися по EXTI: виконання продовжиться з наступного рядка ---
    SystemClock_Config();       // після STOP тактування треба підняти заново
    HAL_ResumeTick();
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    HAL_Delay(60000);           // разовий прогрів давача перед роботою

    while (1) {
        go_to_sleep();          // засинаємо; повертаємось сюди після руху

        if (motion_flag) {
            motion_flag = 0;
            HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_SET);
            HAL_Delay(300);
            HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_RESET);
            // тут — корисна робота, після чого цикл знову приспить МК
        }
    }
}
