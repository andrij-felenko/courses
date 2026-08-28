/* ── flicker.c ── та сама логіка, але вибірку веде ЗАЛІЗО: таймер запускає
   ADC, DMA приносить число, а рахунок робиться просто в callback. Головний
   цикл при цьому вільний — і жодна довга операція не зіб'є частоту вибірки. */
typedef struct {
    float    lo, hi;          /* смуга «вогняних» частот, Гц */
    float    mean, hyst;
    bool     prev_above;
    uint16_t crossings;
    uint32_t win_start;       /* мс, HAL_GetTick() */
    float    last_freq;
} flicker_t;

flicker_t flick = { .lo = 2.0f, .hi = 20.0f, .hyst = 32.0f };  /* 12 біт → ширша зона */
static volatile uint16_t adc_raw;         /* сюди DMA кладе кожну вибірку */

/* TIM3 зведений у CubeMX на 200 Гц і віддає TRGO як тригер ADC1;
   на старті — HAL_ADC_Start_DMA(&hadc1, (uint32_t *)&adc_raw, 1). */
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc) {
    if (hadc->Instance != ADC1) return;
    float v = (float)adc_raw;

    const float alpha = 0.02f;            /* «важке» середнє: йде за рівнем, не за пульсом */
    flick.mean += alpha * (v - flick.mean);

    /* Перетин знизу вгору з гістерезисом — той самий тригер Шмітта в коді. */
    if (!flick.prev_above && v > flick.mean + flick.hyst) { flick.crossings++; flick.prev_above = true; }
    else if (flick.prev_above && v < flick.mean - flick.hyst) flick.prev_above = false;

    uint32_t now = HAL_GetTick(), dt = now - flick.win_start;
    if (dt >= 1000) {                     /* вікно 1 с */
        flick.last_freq = (flick.crossings * 1000.0f) / (float)dt;
        flick.crossings = 0;
        flick.win_start = now;
    }
}

bool flicker_flame(void) { return flick.last_freq >= flick.lo && flick.last_freq <= flick.hi; }
int  flicker_level(void) { return (int)flick.mean; }
