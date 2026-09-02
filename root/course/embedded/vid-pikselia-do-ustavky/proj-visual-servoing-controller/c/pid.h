#ifndef PID_H
#define PID_H

#include <stdbool.h>

/* ПІД-регулятор контуру супроводу.
 *
 * Три відхилення від підручникового: похідна береться за ВИМІРЮВАННЯМ (щоб
 * стрибок рамки детектора не давав удару в мотори), інтегратор має і межу,
 * і умовне накопичення (у насиченні не росте в бік насичення), а зона
 * нечутливості віднімається, а не обнуляє похибку — інакше на її краю вихід
 * стрибав би на kp·deadband. */
typedef struct {
    float kp;
    float ki;
    float kd;
    float max_output;
    float max_integral;
    float deadband;
    float integral;
    float prev_meas;
    bool  primed;
} ServoingPid;

void  pid_init(ServoingPid *pid, float kp, float ki, float kd,
               float max_output, float max_integral, float deadband);
void  pid_reset(ServoingPid *pid);
float pid_update(ServoingPid *pid, float setpoint, float measurement, float dt);

#endif /* PID_H */
