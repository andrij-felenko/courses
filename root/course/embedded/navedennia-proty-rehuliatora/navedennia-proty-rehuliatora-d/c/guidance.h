#ifndef GUIDANCE_H
#define GUIDANCE_H

#include <stdbool.h>
#include <stdint.h>

#include "linalg.h"
#include "setpoint.h"

/* Усе, що наведення знає про світ: повільна навігаційна картина в NED. */
typedef struct {
    Vec3  pos_ned;   /* м, вісь Z спрямована ВНИЗ */
    Vec3  vel_ned;   /* м/с */
    float yaw_rad;   /* поточний курс (для розв'язки осей уставки) */
} NavState;

typedef struct {
    Vec3 vel_integral;   /* інтегратор петлі швидкості, м/с^2 */
    Quat q_prev;         /* попередня уставка — вхід обмежувача швидкості зміни */
    bool primed;
} Guidance;

void guidance_init(Guidance *g);

/* Один такт зовнішнього контуру (20–50 Гц).
   actuators_saturated — прапорець знизу: мотори вперлися, інтегрувати не можна. */
Setpoint guidance_step(Guidance *g,
                       const NavState *nav,
                       Vec3 target_pos_ned,
                       float yaw_sp_rad,
                       float dt,
                       bool actuators_saturated,
                       uint64_t now_us);

#endif /* GUIDANCE_H */
