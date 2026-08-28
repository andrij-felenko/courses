#include "main.h"
#include <stdio.h>

extern TIM_HandleTypeDef  htim2;    // вільний лічильник із тактом 1 мкс
extern UART_HandleTypeDef huart2;

#define TRIG_PORT GPIOA
#define TRIG_PIN  GPIO_PIN_5
#define ECHO_PORT GPIOA
#define ECHO_PIN  GPIO_PIN_6
#define ECHO_TIMEOUT_MS 30          // ~5 м межі дальності
static RangeFilter rf;

static void delay_us(uint16_t us) {                     // мікросекунди — з TIM2
    uint16_t t0 = __HAL_TIM_GET_COUNTER(&htim2);
    while ((uint16_t)(__HAL_TIM_GET_COUNTER(&htim2) - t0) < us) { }
}

// Один відлік: відстань за часом луни + сила (тут — проксі; реальну дає давач).
static Sample read_ranger(void) {
    Sample s = { 0 };                                   // valid = false, поки луни нема
    s.t_ms = HAL_GetTick();                             // мітка часу САМОГО виміру
    HAL_GPIO_WritePin(TRIG_PORT, TRIG_PIN, GPIO_PIN_RESET); delay_us(2);
    HAL_GPIO_WritePin(TRIG_PORT, TRIG_PIN, GPIO_PIN_SET);   delay_us(10);
    HAL_GPIO_WritePin(TRIG_PORT, TRIG_PIN, GPIO_PIN_RESET);

    uint32_t t0 = HAL_GetTick();
    while (HAL_GPIO_ReadPin(ECHO_PORT, ECHO_PIN) == GPIO_PIN_RESET)   // чекаємо фронт
        if (HAL_GetTick() - t0 > ECHO_TIMEOUT_MS) return s;
    uint16_t rise = __HAL_TIM_GET_COUNTER(&htim2);
    while (HAL_GPIO_ReadPin(ECHO_PORT, ECHO_PIN) == GPIO_PIN_SET)     // ширина імпульсу
        if (HAL_GetTick() - t0 > ECHO_TIMEOUT_MS) return s;
    uint32_t us = (uint16_t)(__HAL_TIM_GET_COUNTER(&htim2) - rise);

    s.dist_mm  = (uint16_t)(us * 343UL / 2000UL);   // мкс → мм за c = 343 м/с, шлях туди-й-назад
    s.strength = read_echo_strength();              // АЦП піка луни / signal-rate ToF-давача
    s.valid    = true;
    return s;
}

int main(void) {
    HAL_Init(); SystemClock_Config();
    MX_GPIO_Init(); MX_TIM2_Init(); MX_USART2_UART_Init();
    HAL_TIM_Base_Start(&htim2);
    rf_init(&rf, 1500, 200, 800);   // зближення ≤1.5 м/с; підлога/стеля сили — за калібруванням

    uint32_t next = HAL_GetTick();
    while (1) {
        RangeResult r = rf_update(&rf, read_ranger());
        char line[72]; int n = 0;
        switch (r.status) {
            case RF_FRESH:   // r.med_mm → керування (край), r.mm → показ (гладко)
                n = snprintf(line, sizeof line, "d=%u мм | гладко %u | довіра %d%%\r\n",
                             r.med_mm, r.mm, (int)(r.conf * 100.0f + 0.5f));
                break;
            case RF_HELD:
                n = snprintf(line, sizeof line, "тримаю %u мм (пропуск/викид)\r\n", r.mm);
                break;
            case RF_LOST:
                n = snprintf(line, sizeof line, "ВІДСТАНЬ НЕВІДОМА -> стоп/обережно\r\n");
                break;
        }
        HAL_UART_Transmit(&huart2, (uint8_t *)line, n, 100);
        next += 20;                                     // ~50 Гц без дрейфу періоду
        while ((int32_t)(HAL_GetTick() - next) < 0) { }
    }
}
