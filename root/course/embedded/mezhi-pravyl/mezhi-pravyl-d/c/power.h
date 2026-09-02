#ifndef POWER_H
#define POWER_H

#include "rover.h"

/* Електромеханічний зв'язок: V_term = E_ocv − I_total·ESR.
 * Саме через цю модель правило обходу перешкоди й правило захисту батареї
 * б'ються за той самий ресурс — сумарний струм пакета. */

typedef struct {
    float propulsion_a; /* струм на поздовжню тягу (обидва борти) */
    float yaw_a;        /* струм на диференційний момент рискання */
    float total_a;
    float terminal_v;   /* прогноз напруги на клемах під цим навантаженням */
} PowerDraw;

/* Поздовжня сила опору на швидкості v (кочення + квадратичний опір). */
float power_drag_force(const RoverParams *p, float v);

/* Момент, який мусять дати мотори, щоб на такті dt вийти на yaw_rate_cmd:
 * інерція + тертя ковзання + компенсація вітрового моменту. */
float power_yaw_torque(const RoverParams *p, const VehicleState *st,
                       float yaw_rate_cmd, float dt);

/* Обернена задача: яку кутову швидкість дає дозволений момент torque_nm. */
float power_yaw_rate_for_torque(const RoverParams *p, const VehicleState *st,
                                float torque_nm, float dt);

/* Струм обох бортів на диференційний момент torque_nm. */
float power_yaw_current(const RoverParams *p, float torque_nm);

/* Прогноз споживання, якщо на такті dt виконати команду cmd зі стану st. */
PowerDraw power_predict(const RoverParams *p, const VehicleState *st,
                        Setpoint cmd, float dt);

/* Скільки струму дозволено взяти, поки клеми не просіли під pack_min_v. */
float power_budget_a(const SafetyLimits *lim, const VehicleState *st);

#endif /* POWER_H */
