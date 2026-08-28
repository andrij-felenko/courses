#include <math.h>
// fra_point_t {f, mag_db, phase_deg} оголошено вище, у проході по сітці.

// Лінійна інтерполяція по логарифму частоти між двома точками для рівня y0.
static float interp_logf(float f1, float y1, float f2, float y2, float y0) {
    float t = (y0 - y1) / (y2 - y1);                 // частка шляху від точки 1 до 2
    return f1 * powf(f2 / f1, t);                     // інтерполяція в лог-частоті
}

typedef struct { float fc, pm, f180, gm_db; int ok; } fra_margins_t;

fra_margins_t fra_find_margins(const fra_point_t *p, int n)
{
    fra_margins_t m = { 0, 0, 0, 0, 0 };

    // --- кросовер: перший перехід |L| через 0 дБ згори вниз ---
    for (int i = 1; i < n; i++) {
        if (p[i-1].mag_db >= 0.0f && p[i].mag_db < 0.0f) {
            m.fc = interp_logf(p[i-1].f, p[i-1].mag_db, p[i].f, p[i].mag_db, 0.0f);
            // фазу в точці кросовера інтерполюємо так само, по лог-частоті
            float t  = logf(m.fc / p[i-1].f) / logf(p[i].f / p[i-1].f);
            float ph = p[i-1].phase_deg + t * (p[i].phase_deg - p[i-1].phase_deg);
            m.pm = ph + 180.0f;          // запас по фазі = фаза на кросовері + 180°
            m.ok = 1;
            break;
        }
    }

    // --- точка −180°: перший перехід фази через −180° ---
    for (int i = 1; i < n; i++) {
        if (p[i-1].phase_deg >= -180.0f && p[i].phase_deg < -180.0f) {
            m.f180 = interp_logf(p[i-1].f, p[i-1].phase_deg,
                                 p[i].f, p[i].phase_deg, -180.0f);
            float t   = logf(m.f180 / p[i-1].f) / logf(p[i].f / p[i-1].f);
            float mag = p[i-1].mag_db + t * (p[i].mag_db - p[i-1].mag_db);
            m.gm_db = -mag;              // запас по підсиленню = наскільки |L| нижче 0 дБ
            break;
        }
    }
    return m;
}
