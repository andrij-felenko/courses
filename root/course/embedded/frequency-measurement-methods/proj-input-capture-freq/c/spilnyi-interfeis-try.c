typedef enum { FM_PERIOD, FM_COUNT, FM_RECIPROCAL } fm_method_t;

typedef struct {
    fm_method_t method;
    uint32_t    window_ticks;   // вікно для прямого/реципрокного методу
} fm_cfg_t;

// Єдина точка читання: повертає частоту або 0.0, якщо даних ще нема.
float fm_read_hz(const fm_cfg_t *cfg)
{
    switch (cfg->method) {
    case FM_PERIOD:     return period_read_hz();
    case FM_COUNT:      return count_read_hz(cfg->window_ticks);
    case FM_RECIPROCAL: return reciprocal_read_hz();
    }
    return 0.0f;
}

// Автовибір методу за грубою оцінкою частоти (одне попереднє вимірювання періодом).
fm_method_t fm_pick_method(float rough_hz)
{
    if (rough_hz < 1.0f)      return FM_PERIOD;      // дуже повільно — лови період
    if (rough_hz > 50000.0f)  return FM_COUNT;       // дуже швидко — лічи події
    return FM_RECIPROCAL;                            // широка середина — реципрокно
}
