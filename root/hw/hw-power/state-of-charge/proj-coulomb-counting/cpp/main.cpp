#define DT        0.100f          // крок інтегрування, с (стабільний таймер!)
static float Q;                   // накопичений заряд, А·с (Кл)
static float cap   = 7200.0f;     // вивчена ємність, Кл (2000 мА·год); оновлюється
static float i_zero;              // зсув АЦП при нульовому струмі, А

static float clampf(float x, float lo, float hi) {
    return x < lo ? lo : (x > hi ? hi : x);
}

// раз на DT (з таймера/ISR): один крок лічби
void coulomb_step(void) {
    float i = read_current_A() - i_zero;        // струм зі знаком, мінус зсув нуля
    Q = clampf(Q + i * DT, 0.0f, cap);          // інтеграл з обмеженням
}
float soc_percent(void) { return 100.0f * Q / cap; }

// якір: термінація заряду — комірка точно повна
void on_full_charge(bool full_cycle) {
    Q = cap;                                     // SoC = 100%, дрейф обнулено
    if (full_cycle) cap = relearn_capacity();    // вивчення реальної ємності
}

// якір: відсічка розряду — комірка точно порожня
void on_cutoff(void) { Q = 0.0f; }               // SoC = 0%

// напругова корекція у спокої: комірка відпочила → напруга надійна
void on_rest(void) {
    float q_v = soc_from_ocv(read_voltage_V()) * cap;  // модель/таблиця OCV→SoC
    const float k = 0.02f;                       // м'яко: 0 < k << 1
    Q += k * (q_v - Q);                          // підтягуємо Q до напругової оцінки
}
