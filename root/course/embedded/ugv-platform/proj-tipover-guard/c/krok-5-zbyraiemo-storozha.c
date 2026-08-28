#include <stdint.h>
#include <stdbool.h>
#include <math.h>

// ── Геометрія шасі (під конкретний ровер) ──
#define TRACK_M      0.30f     // колія b, м
#define COG_H_M      0.12f     // висота центра мас h над віссю коліс, м
#define WORK_FRAC    0.50f     // робоча межа = ця частка від статичного φ_crit

// ── Фільтр нахилу ──
#define IMU_DT       0.01f     // крок циклу IMU, с (100 Гц)
#define COMP_TAU     0.50f     // стала комплементарного фільтра, с

// ── Форма придушення ──
#define DEAD         0.50f     // спокійна зона: до цього запасу керма не чіпаємо

// ── Тривога (гістерезис) ──
#define ALARM_ON     0.75f
#define ALARM_OFF    0.60f

typedef struct {
    float roll, pitch;         // згладжені кути нахилу (рад)
    float phi_crit;            // статичний критичний кут (рад), рахуємо раз
    float phi_work;            // робоча межа (рад) = WORK_FRAC · phi_crit
    bool  alarm;               // стан звукової тривоги (з гістерезисом)
    bool  inited;              // фільтр уже засіяний абсолютним кутом?
} tipover_t;

// Ініціалізація: критичний кут з геометрії — раз при старті.
void tipover_init(tipover_t *g) {
    g->roll = g->pitch = 0.0f;
    g->phi_crit = atan2f(TRACK_M * 0.5f, COG_H_M);  // arctan((b/2)/h)
    g->phi_work = WORK_FRAC * g->phi_crit;
    g->alarm = false;
    g->inited = false;
}
