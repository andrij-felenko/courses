// Медіана трьох цілих: жодного множення, отже жодного переповнення.
static inline int32_t median3(int32_t a, int32_t b, int32_t c) {
    // сортувальна мережа з трьох порівнянь-обмінів; лишається середнє
    if (a > b) { int32_t t = a; a = b; b = t; }
    if (b > c) { int32_t t = b; b = c; c = t; }
    if (a > b) { int32_t t = a; a = b; b = t; }
    return b;                 // b тепер — середнє за величиною
}

typedef struct { int32_t w0, w1, w2; } med3_t;   // вікно з трьох відліків

int32_t med3_step(med3_t *m, int32_t x) {
    m->w0 = m->w1;  m->w1 = m->w2;  m->w2 = x;    // зсуваємо вікно
    return median3(m->w0, m->w1, m->w2);
}
