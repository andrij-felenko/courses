// цілий квадратний корінь (для нормування без апаратного sqrt)
static uint32_t isqrt32(uint32_t v) {
    uint32_t r = 0, bit = 1UL << 30;
    while (bit > v) bit >>= 2;
    while (bit) {
        if (v >= r + bit) { v -= r + bit; r = (r >> 1) + bit; }
        else r >>= 1;
        bit >>= 2;
    }
    return r;
}

// нормування Q15-кватерніона: q ← q / |q|
void quat_normalize_q15(quat_q15 *q) {
    int32_t n2 = (int32_t)q->w*q->w + (int32_t)q->x*q->x
               + (int32_t)q->y*q->y + (int32_t)q->z*q->z;   // Q30
    if (n2 <= 0) { q->w = Q15_ONE - 1; q->x = q->y = q->z = 0; return; }
    // |q| у Q15: корінь із Q30 дає Q15
    uint32_t norm = isqrt32((uint32_t)n2);
    if (norm == 0) return;
    // q / |q| : ділимо Q15 на Q15 → множимо на Q15/norm
    q->w = (int16_t)(((int32_t)q->w << 15) / (int32_t)norm);
    q->x = (int16_t)(((int32_t)q->x << 15) / (int32_t)norm);
    q->y = (int16_t)(((int32_t)q->y << 15) / (int32_t)norm);
    q->z = (int16_t)(((int32_t)q->z << 15) / (int32_t)norm);
}
