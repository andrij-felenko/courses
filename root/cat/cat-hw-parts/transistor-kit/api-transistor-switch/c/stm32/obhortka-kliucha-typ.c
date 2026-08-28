// Те саме на STM32 HAL. «Пін» тут — пара порт + маска, решта логіки та сама.
#include "stm32f4xx_hal.h"
#include <stdbool.h>

typedef struct {
    GPIO_TypeDef *port;
    uint16_t      pin;         // GPIO_PIN_0 … GPIO_PIN_15
    bool          active_low;  // true → PNP верхом: рівень «0» вмикає
    bool          on;
} sw_t;

static void sw_on(sw_t *s) {
    HAL_GPIO_WritePin(s->port, s->pin, s->active_low ? GPIO_PIN_RESET : GPIO_PIN_SET);
    s->on = true;
}
static void sw_off(sw_t *s) {
    HAL_GPIO_WritePin(s->port, s->pin, s->active_low ? GPIO_PIN_SET : GPIO_PIN_RESET);
    s->on = false;
}

static void sw_begin(sw_t *s) {
    __HAL_RCC_GPIOB_CLK_ENABLE();     // без такту на порт запис нікуди не піде
    sw_off(s);                        // спершу потрібний рівень у регістрі виходу…
    GPIO_InitTypeDef io = {
        .Pin   = s->pin,
        .Mode  = GPIO_MODE_OUTPUT_PP,
        .Pull  = GPIO_NOPULL,
        .Speed = GPIO_SPEED_FREQ_LOW,
    };
    HAL_GPIO_Init(s->port, &io);      // …і аж потім вивід стає виходом: без сплеску
}

static void sw_set(sw_t *s, bool state) { state ? sw_on(s) : sw_off(s); }
static void sw_toggle(sw_t *s) { sw_set(s, !s->on); }
