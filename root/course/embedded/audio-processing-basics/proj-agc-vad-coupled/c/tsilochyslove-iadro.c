typedef struct {
    int32_t  gain_q;       // підсилення у Q12 (gain_q = gain · 4096)
    int32_t  target;       // цільовий RMS (ціле, у шкалі рівня)
    // Коефіцієнти згладжування — зсувами (замість a_atk/a_rel як float):
    uint8_t  atk_shift;    // атака:      крок = (want−gain) >> atk_shift (малий shift — швидко)
    uint8_t  rel_shift;    // відпускання: крок = (want−gain) >> rel_shift (більший shift — повільно)
    int32_t  max_gain_q;   // стеля у Q12
    uint16_t hold_frames, hold;
    int32_t  gate_level;   // шумовий поріг (у шкалі рівня)
    bool     frozen;
} agc_vad_i_t;

#define AGC_Q 12

// Рівень (RMS) кадру ПІСЛЯ підсилення, ціле. Реалізацію — з теми (цілий RMS).
static int32_t measure_level_i(const int16_t *buf, int n, int32_t gain_q);

void agc_vad_process_i(agc_vad_i_t *s, int16_t *buf, int n, bool voice)
{
    // 1. Режим — так само, як у float-версії.
    if (voice) { s->hold = s->hold_frames; s->frozen = false; }
    else if (s->hold > 0) { if (--s->hold == 0) s->frozen = true; }

    // 2. Ведення підсилення — лише поки не заморожені, усе в цілих.
    if (!s->frozen) {
        int32_t level = measure_level_i(buf, n, s->gain_q);
        if (level > 0) {
            // want = gain · target / level, у Q12: множимо у 64 біти, потім ділимо.
            int64_t want = ((int64_t)s->gain_q * s->target) / level;
            if (want > s->max_gain_q) want = s->max_gain_q;

            bool going_up = (want > s->gain_q);
            if (going_up && level < s->gate_level)
                want = s->gain_q;                       // шумовий поріг: не піднімати

            int32_t diff  = (int32_t)want - s->gain_q;
            uint8_t shift = going_up ? s->rel_shift : s->atk_shift;
            int32_t step  = diff >> shift;              // арифметичний зсув (зі знаком)
            if (step == 0 && diff != 0)                 // не «застрягти» на малій різниці
                step = (diff > 0) ? 1 : -1;
            s->gain_q += step;
        }
    }

    // 3. Накласти підсилення на буфер, ціле множення + зсув, з насиченням.
    for (int i = 0; i < n; i++) {
        int32_t y = (int32_t)(((int64_t)buf[i] * s->gain_q) >> AGC_Q);
        if (y >  32767) y =  32767;
        if (y < -32768) y = -32768;
        buf[i] = (int16_t)y;
    }
}
