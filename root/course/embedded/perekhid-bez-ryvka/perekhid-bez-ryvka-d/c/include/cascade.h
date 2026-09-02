#ifndef CASCADE_H
#define CASCADE_H

#include "bumpless_pid.h"

/* Каскад «позиція -> швидкість -> кут -> привід».
   Контури рознесені за смугою: кутовий крутиться на кожному швидкому такті,
   швидкісний і позиційний — через подільники (multi-rate). */

typedef struct {
    float position_m;
    float velocity_mps;
    float angle_rad;
} cascade_meas_t;

typedef struct {
    pid_config_t pos;
    pid_config_t vel;
    pid_config_t ang;
    /* Передавальні коефіцієнти між поверхами: вихід зовнішнього контуру
       множиться на них, перш ніж стати уставкою внутрішнього. У формулі
       статті I_velocity = Angle_actual / Kp_angle це і є той дільник. */
    float vel_from_pos_gain;
    float ang_from_vel_gain;
    unsigned pos_div;   /* скільки швидких тактів на один такт позиції */
    unsigned vel_div;
} cascade_config_t;

typedef struct {
    bumpless_pid_t pos;
    bumpless_pid_t vel;
    bumpless_pid_t ang;
    float vel_from_pos_gain;
    float ang_from_vel_gain;
    unsigned pos_div;
    unsigned vel_div;
    unsigned tick;
    float vel_sp;
    float ang_sp;
    float last_actuator;
} cascade_t;

void cascade_init(cascade_t *c, const cascade_config_t *cfg);

/* Половини транзакції. Нарізно їх викликає лише демонстрація розірваного
   переходу; у польоті працює cascade_handover(), який робить обидві разом. */
void cascade_load_inner(cascade_t *c, const cascade_meas_t *m, float prev_actuator);
void cascade_load_outer(cascade_t *c, const cascade_meas_t *m, float target_position);

void cascade_handover(cascade_t *c, const cascade_meas_t *m,
                      float target_position, float prev_actuator);
void cascade_start_naive(cascade_t *c, float target_position);

float cascade_update(cascade_t *c, const cascade_meas_t *m, float dt_fast);

#endif /* CASCADE_H */
