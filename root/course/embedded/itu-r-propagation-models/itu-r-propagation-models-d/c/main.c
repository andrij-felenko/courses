#include <math.h>

// Втрати за міською моделлю Хати, дБ.
// f — МГц (150..1500), hb — м (30..200), hm — м (1..10), d — км (1..20)
float hata_urban_db(float f, float hb, float hm, float d) {
    // поправка на висоту мобільної антени (середнє місто)
    float a_hm = (1.1f * log10f(f) - 0.7f) * hm
               - (1.56f * log10f(f) - 0.8f);

    float L = 69.55f
            + 26.16f * log10f(f)
            - 13.82f * log10f(hb)
            - a_hm
            + (44.9f - 6.55f * log10f(hb)) * log10f(d);
    return L;
}

void example(void) {
    float L = hata_urban_db(900.0f, 30.0f, 1.5f, 2.0f);
    // L ≈ 137 дБ — порахуй і порівняй із вакуумом на 2 км/900 МГц (≈ 97 дБ):
    // місто з'їдає на ~40 дБ більше, ніж обіцяє вільний простір!
}
