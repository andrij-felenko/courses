#include "stm32f4xx_hal.h"
#include <stdbool.h>

typedef struct {
    GPIO_TypeDef *port;
    uint16_t      pin;
    uint16_t      debounce_ms;  // скільки стан має протриматись, щоб його прийняти
    bool          raw_last, stable;
    uint32_t      changed_at;   // мітка HAL_GetTick(), мс
} IrObstacle;

// Сирий біт → логічна «перешкода»: активний нуль, тож RESET = true.
static bool IrReadRaw(const IrObstacle *s) {
    return HAL_GPIO_ReadPin(s->port, s->pin) == GPIO_PIN_RESET;
}

// Такт порту (__HAL_RCC_GPIOx_CLK_ENABLE) має бути вже ввімкнений.
void IrObstacle_Begin(IrObstacle *s, GPIO_TypeDef *port, uint16_t pin,
                      uint16_t debounce_ms, bool usePullup) {
    s->port = port;  s->pin = pin;  s->debounce_ms = debounce_ms;
    GPIO_InitTypeDef gi = {0};
    gi.Pin  = pin;
    gi.Mode = GPIO_MODE_INPUT;
    // внутрішня підтяжка лікує «плаваючу» лінію
    gi.Pull = usePullup ? GPIO_PULLUP : GPIO_NOPULL;
    HAL_GPIO_Init(port, &gi);
    // початковий стан читаємо одразу, щоб не «клацнути» на старті
    s->raw_last = s->stable = IrReadRaw(s);
    s->changed_at = HAL_GetTick();
}

// Викликати часто (кожен оберт while(1) або з такту таймера).
void IrObstacle_Update(IrObstacle *s) {
    bool     raw = IrReadRaw(s);
    uint32_t now = HAL_GetTick();
    if (raw != s->raw_last) {              // сирий стан щойно смикнувся
        s->raw_last   = raw;
        s->changed_at = now;               // перезапускаємо відлік стабільності
    }
    // прийняти новий стан лише коли він протримався досить довго
    if (raw != s->stable && (now - s->changed_at) >= s->debounce_ms)
        s->stable = raw;
}

// Чесна подія: true = перешкода поруч (інверсію вже враховано).
bool IrObstacle_Obstacle(const IrObstacle *s) { return s->stable; }
