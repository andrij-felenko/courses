/* ── ky026.h ── STM32 HAL: DO — GPIO-вхід, AO — канал ADC, час — HAL_GetTick */
#pragma once
#include "stm32f4xx_hal.h"
#include <stdbool.h>

typedef struct {
    GPIO_TypeDef      *port_do;   /* напр. GPIOA */
    uint16_t           pin_do;    /* напр. GPIO_PIN_2 */
    ADC_HandleTypeDef *hadc;      /* АЦП, зведений CubeMX на вивід AO */
    bool      inverted;           /* спокій=SET, вогонь=RESET */
    uint32_t  debounce_ms;
    bool      stable, last_raw;
    uint32_t  changed_at;
} ky026_t;

/* Сирий біт «поріг перейдено», уже розвернутий під інверсію. */
static inline bool ky026_raw(const ky026_t *s) {
    GPIO_PinState v = HAL_GPIO_ReadPin(s->port_do, s->pin_do);
    return s->inverted ? (v == GPIO_PIN_RESET) : (v == GPIO_PIN_SET);
}

static inline void ky026_begin(ky026_t *s) {
    /* Такт порту й режим виводу (GPIO_MODE_INPUT, GPIO_NOPULL) уже задано
       в MX_GPIO_Init(); поріг DO задає гвинтик на платі, а не код. */
    s->stable = s->last_raw = ky026_raw(s);
    s->changed_at = HAL_GetTick();             /* мілісекунди від старту */
}

/* Кликати часто з головного циклу — той самий секундомір придушення дрижання. */
static inline bool ky026_update(ky026_t *s) {
    bool now = ky026_raw(s);
    uint32_t t = HAL_GetTick();
    if (now != s->last_raw) { s->last_raw = now; s->changed_at = t; }
    else if (now != s->stable && (t - s->changed_at) >= s->debounce_ms) s->stable = now;
    return s->stable;
}

static inline int ky026_strength(ky026_t *s) {
    HAL_ADC_Start(s->hadc);
    HAL_ADC_PollForConversion(s->hadc, 10);    /* 10 мс стелі — з головою */
    int raw = (int)HAL_ADC_GetValue(s->hadc);  /* сира сила жару, 0..4095 */
    HAL_ADC_Stop(s->hadc);
    return raw;
}
