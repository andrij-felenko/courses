#ifndef MIXER_H
#define MIXER_H

#include <stdbool.h>

#include "linalg.h"

#define MOTOR_COUNT 4
#define MOTOR_IDLE  0.05f

typedef struct {
    float motor[MOTOR_COUNT];  /* нормовані команди 0..1 на ESC */
    bool  saturated;           /* довелося врізати момент або зсунути газ */
} MixerOutput;

/* Квадрокоптер у схемі X, порядок моторів:
     0 — передній правий, 1 — задній лівий, 2 — передній лівий, 3 — задній правий. */
MixerOutput mixer_quad_x(Vec3 torque, float thrust);

/* Зворотне перетворення команд у момент і тягу — потрібне імітатору
   (і бортовому логеру, коли треба побачити, що НАСПРАВДІ дісталося рами). */
void mixer_to_wrench(const float motor[MOTOR_COUNT], Vec3 *torque_out, float *thrust_out);

#endif /* MIXER_H */
