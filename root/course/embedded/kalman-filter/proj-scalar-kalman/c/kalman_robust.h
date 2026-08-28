// kalman_robust.h — захищена обгортка: температурна поправка + ворота на викид.
#ifndef KALMAN_ROBUST_H
#define KALMAN_ROBUST_H

#include "kalman2.h"

typedef struct {
    kalman2_t kf;        // двозмінний фільтр усередині
    float T0;            // опорна температура (за неї міряли нуль), °C
    float kT;            // температурний нахил зсуву, [одиниця величини]/°C
    float gate;          // ворота: множник сигм для відсіву викиду (≈ 3)
    float last_innov;    // остання нев'язка — назовні для діагностики
    uint32_t rejected;   // лічильник відкинутих викидів (теж для логів)
} kalman_robust_t;

void  kr_init(kalman_robust_t *k, float x0,
              float Qx, float Qb, float R, float gate);
void  kr_set_temp_model(kalman_robust_t *k, float T0, float kT);

// Один такт. z_raw — сирий відлік давача; temp_C — поточна температура
// кристала (передай NAN, якщо температурної поправки не треба).
float kr_step(kalman_robust_t *k, float z_raw, float temp_C);

#endif // KALMAN_ROBUST_H
