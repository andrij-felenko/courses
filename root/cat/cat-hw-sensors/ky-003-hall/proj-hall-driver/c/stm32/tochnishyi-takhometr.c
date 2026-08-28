#include "main.h"
extern TIM_HandleTypeDef htim2;   // TIM2 CH1 у режимі Input Capture, спадний фронт;
                                  // прескалер підібрано так, щоб такт = 1 мкс
#define POLES   1
#define STOP_US 2000000u

volatile uint32_t lastEdge = 0;   // захоплений такт попереднього фронту
volatile uint32_t period   = 0;   // останній виміряний період, мкс
volatile uint8_t  gotPulse = 0;

/* мітку часу знімає сам таймер — програма дізнається про фронт уже з нею */
void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance != TIM2) return;
    uint32_t now = HAL_TIM_ReadCapturedValue(htim, TIM_CHANNEL_1);
    if (lastEdge != 0) {          // перший фронт лише задає початок відліку
        period   = now - lastEdge;   // TIM2 32-бітний → різниця вірна й через переповнення
        gotPulse = 1;
    }
    lastEdge = now;
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_TIM2_Init();
    HAL_TIM_IC_Start_IT(&htim2, TIM_CHANNEL_1);

    while (1) {
        __disable_irq();
        uint32_t T = period, last = lastEdge;
        uint8_t  fresh = gotPulse;
        gotPulse = 0;
        __enable_irq();

        if (__HAL_TIM_GET_COUNTER(&htim2) - last > STOP_US) {
            printf("RPM: 0.0\r\n");               // давно немає імпульсів — вал стоїть
        } else if (fresh && T > 0) {
            printf("RPM: %.1f\r\n", 60000000.0f / ((float)T * POLES));
        }                                         // інакше нового періоду ще нема
        HAL_Delay(100);
    }
}
