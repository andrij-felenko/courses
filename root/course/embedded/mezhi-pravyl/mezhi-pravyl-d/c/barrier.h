#ifndef BARRIER_H
#define BARRIER_H

#include "rover.h"

/* Детермінований фільтр безпеки: приймає кандидата від планувальника
 * й повертає уставку, що не порушує жодного фізичного інваріанта.
 * Виконання — O(1), без циклів невідомої довжини й без виділення пам'яті. */

typedef enum {
    BARRIER_PASS,            /* кандидат пройшов без спотворень */
    BARRIER_SPEED_CLAMPED,   /* бар'єр гальмівного шляху */
    BARRIER_POWER_LIMITED,   /* тягу обрізав струмовий бюджет пакета */
    BARRIER_YAW_LIMITED,     /* на потрібний момент рискання струму не вистачає */
    BARRIER_TILT_LIMITED,    /* нахил платформи поза межею */
    BARRIER_EMERGENCY_STOP   /* стан ПОЗА безпечною множиною: h(x) < 0 */
} BarrierVerdict;

typedef struct {
    Setpoint       out;
    BarrierVerdict verdict;
    float          h_value;     /* значення бар'єрної функції h(x) */
    float          budget_a;    /* доступний струм */
    float          predicted_a; /* струм, який візьме видана уставка */
} BarrierResult;

/* h(x) = d_obs − d_safe − v²/(2·a_brake) — запас над гальмівним шляхом. */
float barrier_h(const SafetyLimits *lim, const VehicleState *st);

BarrierResult barrier_enforce(const RoverParams *p, const SafetyLimits *lim,
                              const VehicleState *st, Setpoint candidate, float dt);

const char *barrier_verdict_name(BarrierVerdict v);

#endif /* BARRIER_H */
