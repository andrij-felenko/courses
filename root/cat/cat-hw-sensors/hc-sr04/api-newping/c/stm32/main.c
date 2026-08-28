// STM32 HAL. ECHO — ТІЛЬКИ через подільник 1к/2к (5 В → ~3.3 В), VCC модуля — 5 В.
// TIM1 налаштований у CubeMX так, щоб лічильник цокав раз на мікросекунду
// (Prescaler = такт_таймера_в_МГц − 1, Period = 0xFFFF) — це наше джерело часу.
#include "main.h"
#include <stdio.h>

extern TIM_HandleTypeDef  htim1;
extern UART_HandleTypeDef huart2;

#define TRIG_PORT        GPIOA
#define TRIG_PIN         GPIO_PIN_8
#define ECHO_PORT        GPIOA
#define ECHO_PIN         GPIO_PIN_9
#define ECHO_TIMEOUT_US  40000u          // трохи більше за апаратні ~38 мс модуля

static void delay_us(uint16_t us)
{
    __HAL_TIM_SET_COUNTER(&htim1, 0);
    while (__HAL_TIM_GET_COUNTER(&htim1) < us) { }
}

/* Повертає відстань у см, або 0 — якщо луни не було (порожньо / поза межами). */
static uint16_t measure_cm(void)
{
    /* Такт 1: чистий поштовх 10 мкс. */
    HAL_GPIO_WritePin(TRIG_PORT, TRIG_PIN, GPIO_PIN_RESET); delay_us(2);
    HAL_GPIO_WritePin(TRIG_PORT, TRIG_PIN, GPIO_PIN_SET);   delay_us(10);
    HAL_GPIO_WritePin(TRIG_PORT, TRIG_PIN, GPIO_PIN_RESET);

    /* Такт 2: чекаємо фронту ECHO — з тайм-аутом, інакше зависнемо назавжди. */
    __HAL_TIM_SET_COUNTER(&htim1, 0);
    while (HAL_GPIO_ReadPin(ECHO_PORT, ECHO_PIN) == GPIO_PIN_RESET)
        if (__HAL_TIM_GET_COUNTER(&htim1) > ECHO_TIMEOUT_US) return 0;

    /* Такт 3: міряємо ширину високого рівня, мкс. */
    __HAL_TIM_SET_COUNTER(&htim1, 0);
    while (HAL_GPIO_ReadPin(ECHO_PORT, ECHO_PIN) == GPIO_PIN_SET)
        if (__HAL_TIM_GET_COUNTER(&htim1) > ECHO_TIMEOUT_US) return 0;

    return (uint16_t)(__HAL_TIM_GET_COUNTER(&htim1) / 58);   /* Такт 4: мкс → см */
}

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_TIM1_Init();
    MX_USART2_UART_Init();
    HAL_TIM_Base_Start(&htim1);          /* лічильник мікросекунд пішов */

    char buf[24];
    while (1) {
        uint16_t cm = measure_cm();
        int n = (cm == 0) ? snprintf(buf, sizeof buf, "out of range\r\n")
                          : snprintf(buf, sizeof buf, "%u cm\r\n", cm);
        HAL_UART_Transmit(&huart2, (uint8_t *)buf, n, HAL_MAX_DELAY);
        HAL_Delay(60);                   /* пауза між вимірами ≥ 60 мс */
    }
}
