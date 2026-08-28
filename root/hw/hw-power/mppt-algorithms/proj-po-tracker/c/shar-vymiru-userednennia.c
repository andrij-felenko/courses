// Передискретизація: N сирих відліків → середнє (N — степінь двійки).
#define OVERSAMPLE  16u

static uint16_t adc_avg(uint8_t ch) {
    uint32_t acc = 0;
    for (uint8_t i = 0; i < OVERSAMPLE; ++i)
        acc += adc_read_raw(ch);
    return (uint16_t)(acc / OVERSAMPLE);   // компілятор зробить зсув
}

static inline uint16_t raw_to_mv(uint16_t code) {
    return (uint16_t)(((uint32_t)code * PANEL_V_NUM) / PANEL_V_DEN);
}
static inline uint16_t raw_to_ma(uint16_t code) {
    return (uint16_t)(((uint32_t)code * PANEL_I_NUM) / PANEL_I_DEN);
}

// EMA без втрати молодших бітів: стан у масштабі ×2^k, зсув лише на виході.
//   s += x − (s >> k);   значення = s >> k
typedef struct { int32_t s; bool primed; } ema_t;

static uint16_t ema_upd(ema_t *f, uint16_t x, uint8_t k) {
    if (!f->primed) { f->s = (int32_t)x << k; f->primed = true; }
    f->s += (int32_t)x - (f->s >> k);
    return (uint16_t)(f->s >> k);
}
