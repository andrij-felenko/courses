// kalman_robust.c
#include "kalman_robust.h"
#include <math.h>     // isnan, isfinite

void kr_init(kalman_robust_t *k, float x0,
             float Qx, float Qb, float R, float gate)
{
    kalman2_init(&k->kf, x0, 0.0f, Qx, Qb, R);
    k->T0 = 0.0f;
    k->kT = 0.0f;          // без температурної поправки, поки не задано
    k->gate = gate;        // напр. 3.0 → відсікаємо нев'язку за межами 3σ
    k->last_innov = 0.0f;
    k->rejected = 0;
}

void kr_set_temp_model(kalman_robust_t *k, float T0, float kT)
{
    k->T0 = T0;
    k->kT = kT;
}

float kr_step(kalman_robust_t *k, float z_raw, float temp_C)
{
    kalman2_t *kf = &k->kf;

    // 0) Викид-сміття: не число → нічого не оновлюємо, віддаємо стару оцінку.
    if (!isfinite(z_raw)) {
        k->rejected++;
        return kf->x;
    }

    // 1) Температурна поправка: віднімаємо ВІДОМУ частину дрейфу наперед.
    float z = z_raw;
    if (k->kT != 0.0f && isfinite(temp_C)) {
        z -= k->kT * (temp_C - k->T0);
    }

    // 2) ПЕРЕДБАЧ — як у kalman2, але робимо його тут, бо ворота мусять
    //    бачити вже передбачену непевність (S рахується після росту P).
    kf->P00 += kf->Qx;
    kf->P11 += kf->Qb;

    // 3) Нев'язка та її очікуваний розкид (для воріт і для діагностики).
    float y = z - (kf->x + kf->b);
    float S = kf->P00 + kf->P01 + kf->P10 + kf->P11 + kf->R;
    k->last_innov = y;     // віддаємо назовні: сторожа розходження дивиться сюди

    // 4) ВОРОТА: нев'язка за межами gate·σ → це викид, корекцію пропускаємо.
    //    Порівнюємо квадрати, щоб не брати корінь: y² < gate²·S ?
    if (y * y > k->gate * k->gate * S) {
        k->rejected++;
        return kf->x;      // P уже виросло на кроці 2 → наступний вимір приймемо охочіше
    }

    // 5) ВИПРАВ — корекція, як у kalman2_step (передбач уже зроблено вище).
    float K0 = (kf->P00 + kf->P01) / S;
    float K1 = (kf->P10 + kf->P11) / S;
    kf->x += K0 * y;
    kf->b += K1 * y;

    float P00 = kf->P00, P01 = kf->P01, P10 = kf->P10, P11 = kf->P11;
    kf->P00 = P00 - K0 * (P00 + P10);
    kf->P01 = P01 - K0 * (P01 + P11);
    kf->P10 = P10 - K1 * (P00 + P10);
    kf->P11 = P11 - K1 * (P01 + P11);

    return kf->x;
}
