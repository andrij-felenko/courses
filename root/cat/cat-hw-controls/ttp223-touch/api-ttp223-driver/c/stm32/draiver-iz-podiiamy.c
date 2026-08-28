// --- touch_button: драйвер миттєвого режиму TTP223 (STM32 HAL) --------------
#include "stm32f4xx_hal.h"

#define TOUCH_GUARD_MS  5      // мс стійкості проти імпульсів-привидів

typedef struct {
    GPIO_TypeDef  *port;
    uint16_t       pin;
    GPIO_PinState  active;     // GPIO_PIN_SET (акт. у 1) або GPIO_PIN_RESET
    bool           raw, stable, just_pressed, just_released;
    uint32_t       last_edge, pressed_at;   // тики HAL_GetTick(), тобто мс
} touch_button_t;

static bool tb_read_active(const touch_button_t *b) {
    return HAL_GPIO_ReadPin(b->port, b->pin) == b->active;
}

void tb_begin(touch_button_t *b, GPIO_TypeDef *port, uint16_t pin, GPIO_PinState active) {
    b->port = port; b->pin = pin; b->active = active;
    b->just_pressed = b->just_released = false;

    GPIO_InitTypeDef gpio = {0};          // двотактний вихід → без підтяжки
    gpio.Pin = pin; gpio.Mode = GPIO_MODE_INPUT; gpio.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(port, &gpio);

    b->stable = b->raw = tb_read_active(b);   // старт із поточного стану
    b->last_edge = HAL_GetTick();
}

// Кликати щопроходу циклу; true рівно в момент активації (фронт).
bool tb_update(touch_button_t *b) {
    bool a = tb_read_active(b);
    uint32_t now = HAL_GetTick();

    if (a != b->raw) { b->raw = a; b->last_edge = now; }   // сирий рівень змінився

    if (now - b->last_edge >= TOUCH_GUARD_MS && b->stable != a) {
        b->stable = a;                    // рівень протримався GUARD мс → справжній
        if (a) { b->pressed_at = now; b->just_pressed = true; return true; }
        b->just_released = true;
    }
    return false;
}

bool tb_pressed(touch_button_t *b)  { bool r = b->just_pressed;  b->just_pressed  = false; return r; }
bool tb_released(touch_button_t *b) { bool r = b->just_released; b->just_released = false; return r; }
bool tb_held(const touch_button_t *b)   { return b->stable; }
uint32_t tb_held_ms(const touch_button_t *b) { return b->stable ? HAL_GetTick() - b->pressed_at : 0; }
