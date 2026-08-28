// Термінація NiMH за dT/dt: ловимо різкий нагрів у мить повноти.
#define DTDT_STOP_DC_PER_MIN  10    // поріг 1.0 °C/хв, у десятих °C
#define SAMPLE_S              5     // період вимірювання температури, с

static int16_t  t_prev_dc = 0;      // попередня температура, десяті °C
static uint32_t t_prev_ms = 0;

// cell_temp_dc — температура комірки в десятих градуса (напр., 253 = 25.3 °C)
bool nimh_done(int16_t cell_temp_dc, uint32_t now_ms) {
    if (t_prev_ms == 0) {           // перший виклик — лише запам'ятати
        t_prev_dc = cell_temp_dc;
        t_prev_ms = now_ms;
        return false;
    }
    if (now_ms - t_prev_ms < SAMPLE_S * 1000UL)
        return false;               // ще рано міряти нахил

    int32_t d_temp = cell_temp_dc - t_prev_dc;             // приріст, десяті °C
    int32_t d_min  = (now_ms - t_prev_ms) / 60000;         // час, хвилини (цілі)
    t_prev_dc = cell_temp_dc;
    t_prev_ms = now_ms;

    // нахил у десятих °C за хвилину; ділення бережемо від нуля
    if (d_min > 0 && d_temp / d_min >= DTDT_STOP_DC_PER_MIN)
        return true;                // комірка різко гріється → повна
    return false;
}
