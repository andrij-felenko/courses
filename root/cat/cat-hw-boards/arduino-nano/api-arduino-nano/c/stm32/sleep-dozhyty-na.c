#include "stm32f4xx_hal.h"

extern RTC_HandleTypeDef hrtc;   // джерело такту RTC — LSE 32768 Гц

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_RTC_Init();

    while (1) {
        // 1. корисна робота (тут — блимнути, а реально: виміряти й записати)
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);
        HAL_Delay(20);
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_RESET);

        // 2. звести будильник RTC на 8 с: RTCCLK/16 = 2048 тиків на секунду
        HAL_RTCEx_SetWakeUpTimer_IT(&hrtc, 8 * 2048, RTC_WAKEUPCLOCK_RTCCLK_DIV16);
        HAL_SuspendTick();       // інакше SysTick будив би нас щомілісекунди
        HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);
        // ← а сюди керування повертається: після STOP програма йде далі,
        //   але такт скинуто на HSI — його треба підняти заново
        SystemClock_Config();
        HAL_ResumeTick();
        HAL_RTCEx_DeactivateWakeUpTimer(&hrtc);
    }
}
