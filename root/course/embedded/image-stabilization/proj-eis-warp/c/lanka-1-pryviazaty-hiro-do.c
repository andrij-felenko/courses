#include <stdint.h>
#include <stddef.h>
#include <math.h>

/* Один відлік гіроскопа: час у секундах (за годинником гіро) і три
   кутові швидкості в рад/с навколо осей кадру X (тангаж), Y (рискання), Z (крен). */
typedef struct { double t; double wx, wy, wz; } gyro_sample;

/* Параметри прив'язки часу: зсув (offset) і дрейф годинника (scale ≈ 1). */
typedef struct { double t_off; double scale; } time_sync;

/* Момент кадру (відеочас) → момент у часі гіро. */
static double frame_to_gyro_time(const time_sync *s, double t_frame)
{
    return s->t_off + s->scale * t_frame;   /* пряма, не просто зсув */
}

/* Кутова швидкість гіро в довільний момент tg: лінійна інтерполяція між
   двома сусідніми відліками. n — довжина g, відліки впорядковані за часом. */
static void gyro_at(const gyro_sample *g, size_t n, double tg,
                    double *wx, double *wy, double *wz)
{
    /* за межами логу — тримаємо крайній відлік (екстраполяцію не вигадуємо) */
    if (tg <= g[0].t)     { *wx = g[0].wx;     *wy = g[0].wy;     *wz = g[0].wz;     return; }
    if (tg >= g[n-1].t)   { *wx = g[n-1].wx;   *wy = g[n-1].wy;   *wz = g[n-1].wz;   return; }

    /* двійковий пошук правого сусіда: перший відлік із часом > tg */
    size_t lo = 0, hi = n - 1;
    while (hi - lo > 1) {
        size_t mid = (lo + hi) / 2;
        if (g[mid].t <= tg) lo = mid; else hi = mid;
    }
    /* lo ≤ tg < hi; частка a — наскільки tg просунувся від lo до hi */
    double span = g[hi].t - g[lo].t;
    double a = (span > 1e-12) ? (tg - g[lo].t) / span : 0.0;

    *wx = g[lo].wx + a * (g[hi].wx - g[lo].wx);
    *wy = g[lo].wy + a * (g[hi].wy - g[lo].wy);
    *wz = g[lo].wz + a * (g[hi].wz - g[lo].wz);
}
