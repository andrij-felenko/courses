#ifndef METRICS_H
#define METRICS_H

#include "log.h"
#include "step_detect.h"

typedef struct {
    double amplitude;         /* амплітуда сходинки, deg/s */
    double tau_ms;            /* транспортне запізнення: вихід на 5% */
    double rise_time_ms;      /* час наростання 10% → 90% */
    double overshoot_pct;     /* перерегулювання першого екстремуму */
    double settling_time_ms;  /* вхід у коридор ±5% від початку маневру */
    double d_noise_rms;       /* ВЧ-шум D-терма на плато */
    int    ring_crossings;    /* перетини цільового рівня після піка (дзвін) */
    int    reached_90;        /* чи дотягнув гіроскоп до 90% завдання */
    int    settled;           /* чи ввійшов у коридор до кінця вікна */
    int    noise_measured;    /* чи вистачило плато на оцінку шуму */
} StepMetrics;

/* Обчислює метрики одного вікна. 0 — успіх; -1 — вікно непридатне
   (немає реакції або замало відліків). */
int metrics_compute(const FlightLog *log, const StepWindow *w, StepMetrics *out);

/* Медіана по серії сходинок: один поганий кидок не має вирішувати вердикт.
   0 — успіх, -1 — порожня або задовга серія. */
int metrics_median(const StepMetrics *m, size_t n, StepMetrics *out);

#endif /* METRICS_H */
