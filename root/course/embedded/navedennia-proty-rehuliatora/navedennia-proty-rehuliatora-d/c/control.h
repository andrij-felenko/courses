#ifndef CONTROL_H
#define CONTROL_H

#include <stdbool.h>
#include <stdint.h>

#include "linalg.h"
#include "setpoint.h"

typedef struct {
    Vec3     rate_integral;  /* інтегратор петлі кутових швидкостей */
    Vec3     gyro_prev;
    Vec3     d_filtered;     /* згладжена похідна вимірювання */
    Setpoint last_good;      /* остання цілісна уставка */
    bool     have_setpoint;
    float    thrust_cmd;     /* тримаємо окремо: в аварії тяга плавно повзе вниз */
    bool     fallback;
} Control;

typedef struct {
    Vec3  torque;    /* нормовані моменти -1..1 у зв'язаній системі */
    float thrust;    /* 0..1 */
    bool  fallback;  /* уставка протухла, тримаємо горизонт */
} ControlOutput;

void control_init(Control *c);

/* Один такт внутрішнього контуру (500–1000 Гц, зазвичай з переривання Data Ready).
   Тут немає жодної навігаційної величини — лише кватерніон, гіроскоп і уставка. */
ControlOutput control_step(Control *c,
                           SetpointMailbox *mb,
                           ControlFeedback *fb,
                           Quat q_est,
                           Vec3 gyro_rad_s,
                           float dt,
                           uint64_t now_us);

#endif /* CONTROL_H */
