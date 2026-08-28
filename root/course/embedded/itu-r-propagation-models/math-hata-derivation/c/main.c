#include <math.h>

// Поправка на висоту мобільного (середнє місто) — спільна для Hata і COST 231
static float a_hm_medium(float f, float hm) {
    return (1.1f * log10f(f) - 0.7f) * hm
         - (1.56f * log10f(f) - 0.8f);
}

// COST 231-Hata, дБ.  f — МГц (1500..2000), hb — м (30..200),
// hm — м (1..10), d — км (1..20), big_city — true для метрополії
float cost231_db(float f, float hb, float hm, float d, int big_city) {
    float Cm  = big_city ? 3.0f : 0.0f;
    float L = 46.3f
            + 33.9f * log10f(f)
            - 13.82f * log10f(hb)
            - a_hm_medium(f, hm)
            + (44.9f - 6.55f * log10f(hb)) * log10f(d)
            + Cm;
    return L;
}

void example(void) {
    float L = cost231_db(1800.0f, 30.0f, 1.5f, 2.0f, /*big_city=*/1);
    // L ≈ 149.8 дБ — порівняй із міською Hata на 900 МГц/2 км (≈137 дБ):
    // подвоєння частоти + метрополія додають ще ~12.8 дБ втрат.
}
