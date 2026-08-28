static uint8_t seg_hint = 0;          // де відрізок знайшовся минулого разу

// Повертає індекс i такий, що k[i].v ≤ v ≤ k[i+1].v.
// Викликати ЛИШЕ з v у межах таблиці — межі перевіряє той, хто кличе.
static uint8_t find_segment(const ocv_table_t *t, uint16_t v) {
    uint8_t last = (uint8_t)(t->n - 2);               // індекс останнього відрізка
    uint8_t i = seg_hint > last ? last : seg_hint;

    if (v >= t->k[i].v_01mv && v < t->k[i+1].v_01mv) { seg_hint = i; return i; }
    if (i > 0 && v >= t->k[i-1].v_01mv && v < t->k[i].v_01mv) {
        seg_hint = (uint8_t)(i - 1); return seg_hint;
    }
    if (i < last && v >= t->k[i+1].v_01mv && v < t->k[i+2].v_01mv) {
        seg_hint = (uint8_t)(i + 1); return seg_hint;
    }

    // Промах — двійковий пошук: найбільший i, де k[i].v ≤ v.
    uint8_t lo = 0, hi = last;
    while (lo < hi) {
        uint8_t mid = (uint8_t)(lo + (hi - lo + 1) / 2);   // ВЕРХНЯ середина
        if (t->k[mid].v_01mv <= v) lo = mid; else hi = (uint8_t)(mid - 1);
    }
    seg_hint = lo;
    return lo;
}
