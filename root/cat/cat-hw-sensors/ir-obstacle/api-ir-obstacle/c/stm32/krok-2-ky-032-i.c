#include "stm32f4xx_hal.h"
#include <stdbool.h>

#define EN_ON_MS   1u   // вікно несучої (≤2 мс!)
#define EN_OFF_MS  1u   // пауза для розслаблення AGC

typedef struct {
    GPIO_TypeDef *outPort;  uint16_t outPin;
    GPIO_TypeDef *enPort;   uint16_t enPin;   // enPort = NULL → піна EN нема
    uint16_t      debounce_ms;
    bool          raw_last, stable, en_high;
    uint32_t      changed_at, phase_at;
} IrObstacleEN;

static bool HasEN(const IrObstacleEN *s)   { return s->enPort != NULL; }
static bool ReadRaw(const IrObstacleEN *s) {
    return HAL_GPIO_ReadPin(s->outPort, s->outPin) == GPIO_PIN_RESET;
}

// Такти обох портів (__HAL_RCC_GPIOx_CLK_ENABLE) мають бути ввімкнені.
void IrObstacleEN_Begin(IrObstacleEN *s, GPIO_TypeDef *outPort, uint16_t outPin,
                        GPIO_TypeDef *enPort, uint16_t enPin, uint16_t debounce_ms) {
    s->outPort = outPort;  s->outPin = outPin;
    s->enPort  = enPort;   s->enPin  = enPin;
    s->debounce_ms = debounce_ms;

    GPIO_InitTypeDef gi = {0};
    gi.Pin = outPin;  gi.Mode = GPIO_MODE_INPUT;  gi.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(outPort, &gi);
    if (HasEN(s)) {
        GPIO_InitTypeDef go = {0};
        go.Pin   = enPin;
        go.Mode  = GPIO_MODE_OUTPUT_PP;
        go.Pull  = GPIO_NOPULL;
        go.Speed = GPIO_SPEED_FREQ_LOW;
        HAL_GPIO_Init(enPort, &go);
        HAL_GPIO_WritePin(enPort, enPin, GPIO_PIN_RESET);  // старт без несучої
    }
    s->raw_last = s->stable = ReadRaw(s);
    s->changed_at = s->phase_at = HAL_GetTick();
    s->en_high = false;
}

// Придушення дрижання — те саме, що без EN.
static void DebounceOnly(IrObstacleEN *s, bool raw) {
    uint32_t now = HAL_GetTick();
    if (raw != s->raw_last) { s->raw_last = raw; s->changed_at = now; }
    if (raw != s->stable && (now - s->changed_at) >= s->debounce_ms) s->stable = raw;
}

// Неблокуюча машина станів для EN.
void IrObstacleEN_Update(IrObstacleEN *s) {
    if (!HasEN(s)) { DebounceOnly(s, ReadRaw(s)); return; }
    uint32_t now = HAL_GetTick();
    if (s->en_high) {
        if (now - s->phase_at >= EN_ON_MS) {                          // вікно скінчилось
            DebounceOnly(s, ReadRaw(s));                              // читаємо ПОКИ несуча ще була
            HAL_GPIO_WritePin(s->enPort, s->enPin, GPIO_PIN_RESET);   // гасимо несучу
            s->en_high = false;  s->phase_at = now;
        }
    } else {
        if (now - s->phase_at >= EN_OFF_MS) {                         // пауза скінчилась
            HAL_GPIO_WritePin(s->enPort, s->enPin, GPIO_PIN_SET);     // пускаємо несучу
            s->en_high = true;   s->phase_at = now;
        }
    }
}

bool IrObstacleEN_Obstacle(const IrObstacleEN *s) { return s->stable; }
