// ── Одна KY-027 як плавний індикатор нахилу (STM32 HAL, ШІМ на TIM3_CH1) ──
// TIM3 у CubeMX: ARR = 255 → CCR приймає рівно 0..255.
#include "main.h"
#include <stdbool.h>

extern TIM_HandleTypeDef htim3;

#define PORT_S  GPIOA            // вихід вимикача (цифровий вхід)
#define PIN_S   GPIO_PIN_0
#define CH_L    TIM_CHANNEL_1    // світлодіод — PA6 (TIM3_CH1)
#define TILTED  false            // рівень S, що означає «нахилено»

typedef struct { GPIO_TypeDef *port; uint16_t pin; bool stable, last_raw; uint32_t changed_at; } Debounced;
#define DEBOUNCE_MS 25u

static void DebounceBegin(Debounced *d, GPIO_TypeDef *port, uint16_t pin) {
    d->port = port; d->pin = pin;
    d->stable = (HAL_GPIO_ReadPin(port, pin) == GPIO_PIN_SET);
    d->last_raw = d->stable; d->changed_at = HAL_GetTick();
}
static bool DebounceRead(Debounced *d) {
    bool raw = (HAL_GPIO_ReadPin(d->port, d->pin) == GPIO_PIN_SET);
    if (raw != d->last_raw) { d->last_raw = raw; d->changed_at = HAL_GetTick(); }
    if (raw != d->stable && (HAL_GetTick() - d->changed_at) >= DEBOUNCE_MS) d->stable = raw;
    return d->stable;
}

#define STEP 4

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_TIM3_Init();

    Debounced sw;
    DebounceBegin(&sw, PORT_S, PIN_S);
    HAL_TIM_PWM_Start(&htim3, CH_L);

    uint8_t bright = 0;                  // поточна яскравість 0..255
    while (1) {
        bool tilted = (DebounceRead(&sw) == TILTED);
        // Нахилено → повземо до 255; рівно → сповзаємо до 0. Обидва — з упором.
        int next = (int)bright + (tilted ? +STEP : -STEP);
        if (next < 0) next = 0;
        if (next > 255) next = 255;
        bright = (uint8_t)next;

        __HAL_TIM_SET_COMPARE(&htim3, CH_L, bright);
        HAL_Delay(6);                    // темп наростання/згасання
    }
}
