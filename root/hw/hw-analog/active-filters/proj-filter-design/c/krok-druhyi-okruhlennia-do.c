// Ряд E12 (одна декада, ±10%). Решта декад — множенням на 10.
static const float E12[] = {
    1.0f, 1.2f, 1.5f, 1.8f, 2.2f, 2.7f,
    3.3f, 3.9f, 4.7f, 5.6f, 6.8f, 8.2f
};
#define E12_N (sizeof(E12) / sizeof(E12[0]))

// Найближче значення ряду E12 до x (x > 0). Округлення в лог-масштабі:
// шукаємо мантису й декаду, беремо найближчий E12 за відношенням, не різницею.
static float e12_nearest(float x) {
    float decade = powf(10.0f, floorf(log10f(x)));  // 10^k: масштаб декади
    float m = x / decade;                            // мантиса в [1, 10)
    // найближче за лог-відстанню (рівні множники, не рівні різниці)
    float best = E12[0]; float best_d = 1e9f;
    for (uint32_t i = 0; i < E12_N; i++) {
        float d = fabsf(log10f(m / E12[i]));         // лог-відстань
        if (d < best_d) { best_d = d; best = E12[i]; }
    }
    // мантиса 8.2 і число близько до 10 → перевірити «10.0» наступної декади
    float up = fabsf(log10f(m / 10.0f));
    if (up < best_d) { best = 10.0f; }
    return best * decade;
}

// Перерахувати ФАКТИЧНІ f0 і Q ланки з її R, C1, C2 (прямі формули).
static void sk_actual(sk_stage *s) {
    s->f0 = 1.0f / (2.0f * (float)M_PI * s->R * sqrtf(s->C1 * s->C2));
    s->Q  = 0.5f * sqrtf(s->C1 / s->C2);
}

// Повний підбір: ідеал → округлення обох конденсаторів → фактичні f0, Q.
// На вході s->R, s->f0 (бажана), s->Q (бажана).
// На виході s->C1, s->C2 — стандартні; s->f0, s->Q — фактичні після округлення.
static void sk_design(sk_stage *s) {
    float want_f0 = s->f0, want_Q = s->Q;
    s->f0 = want_f0; s->Q = want_Q;
    sk_pick_caps(s);                  // ідеальні C1, C2
    s->C1 = e12_nearest(s->C1);       // притягуємо до ряду
    s->C2 = e12_nearest(s->C2);
    sk_actual(s);                     // що ВИЙШЛО насправді
}
