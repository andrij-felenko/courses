#include "main.h"                    // HAL, згенерований CubeMX
#include <stdio.h>

#define SHOCK_PORT   GPIOA
#define SHOCK_PIN    GPIO_PIN_0      // нога з лінією EXTI
#define SHOCK_IRQ    EXTI0_IRQn
#define LED_PORT     GPIOC
#define LED_PIN      GPIO_PIN_13

#define DEBOUNCE_MS  60u             // вікно придушення брязкоту

// --- те, що ISR передає головному циклу; усе volatile ---
volatile uint32_t g_edges      = 0;  // скільки фронтів прилетіло всього
volatile uint32_t g_lastEdgeMs = 0;  // час останнього фронту

static uint32_t g_seen = 0, g_shocks = 0, g_lastShock = 0;

// Вектор EXTI (зазвичай лежить у stm32xxxx_it.c) лише передає керування HAL.
void EXTI0_IRQHandler(void) { HAL_GPIO_EXTI_IRQHandler(SHOCK_PIN); }

// А оце — наша ISR. Жодного printf і жодних обчислень.
void HAL_GPIO_EXTI_Callback(uint16_t pin) {
    if (pin != SHOCK_PIN) return;
    g_edges++;
    g_lastEdgeMs = HAL_GetTick();    // тік SysTick іде й у перериванні
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();

    GPIO_InitTypeDef g = {0};
    g.Pin  = LED_PIN;  g.Mode = GPIO_MODE_OUTPUT_PP;  g.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(LED_PORT, &g);

    // Спершу — просто вхід із підтяжкою вгору, щоб зміряти спокій.
    g.Pin = SHOCK_PIN;  g.Mode = GPIO_MODE_INPUT;  g.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(SHOCK_PORT, &g);
    HAL_Delay(50);                                    // дати входу усталитися

    // --- Автовизначення полярності: що плата тримає у спокої? ---
    GPIO_PinState idle = HAL_GPIO_ReadPin(SHOCK_PORT, SHOCK_PIN);
    printf("Рівень спокою = %s\r\n",
           idle == GPIO_PIN_SET ? "HIGH (pull-up варіант)" : "LOW (pull-down варіант)");

    // Перенастроюємо ту саму ногу на фронт, що ВІДХОДИТЬ від спокою.
    g.Mode = (idle == GPIO_PIN_SET) ? GPIO_MODE_IT_FALLING : GPIO_MODE_IT_RISING;
    HAL_GPIO_Init(SHOCK_PORT, &g);
    HAL_NVIC_SetPriority(SHOCK_IRQ, 5, 0);
    HAL_NVIC_EnableIRQ(SHOCK_IRQ);

    printf("Готовий. Струсіть давач.\r\n");

    while (1) {
        // Два пов'язані значення знімаємо цілісно: окремо кожне 32-бітне читання
        // на Cortex-M атомарне, але пара може розійтися між ними.
        uint32_t edges, lastEdge;
        __disable_irq();
        edges    = g_edges;
        lastEdge = g_lastEdgeMs;
        __enable_irq();

        if (edges != g_seen) {                        // прилетіли нові фронти
            g_seen = edges;
            // Придушення брязкоту без HAL_Delay: лише порівняння міток часу.
            if (lastEdge - g_lastShock >= DEBOUNCE_MS) {
                g_lastShock = lastEdge;
                g_shocks++;
                printf("СТРУС #%lu\r\n", (unsigned long)g_shocks);
                HAL_GPIO_WritePin(LED_PORT, LED_PIN, GPIO_PIN_SET);
            }
            // якщо не дотягло до вікна — це відскок пружини, мовчки ігноруємо
        }

        // Погасити світлодіод через 30 мс — теж без блокувальної затримки.
        if (HAL_GetTick() - g_lastShock >= 30)
            HAL_GPIO_WritePin(LED_PORT, LED_PIN, GPIO_PIN_RESET);

        // ...тут головний цикл вільний робити будь-що інше...
    }
}
