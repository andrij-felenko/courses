#ifndef PID_H
#define PID_H

#include <stdbool.h>

/* Налаштування контуру. Вихід і межі інтегратора — у частках тяги 0..1. */
typedef struct {
    float kp, ki, kd;
    float kff;            /* пряма гілка від уставки */
    float out_min, out_max;
    float i_min, i_max;
    float slew_rate_max;  /* м/с; 0 — уставка переставляється стрибком */
} pid_cfg_t;

typedef struct {
    pid_cfg_t cfg;
    float integral;
    float prev_meas;      /* потрібен, коли швидкість треба рахувати чисельно */
    float target_sp;      /* куди хочемо */
    float current_sp;     /* де уставка зараз (після ремпінгу) */
    float last_out;
    bool  ready;
    unsigned bad_samples; /* скільки разів прийшов NaN/inf */
} pid_t;

void  pid_init(pid_t *p, const pid_cfg_t *cfg);

/* Безривкове захоплення. Повертає залишковий стрибок виходу: нуль, якщо
   інтегратор вдалося зарядити точно; ненуль — якщо він уперся в межу;
   NAN — якщо вимір непридатний і захоплення робити не можна. */
float pid_bumpless_handover(pid_t *p, float meas, float meas_rate,
                            float target_sp, float prev_out);

void  pid_retarget(pid_t *p, float target_sp);

/* meas_rate — швидкість зміни виміру від фузії сенсорів; NAN означає
   «нема», тоді похідна рахується чисельно по prev_meas. */
float pid_update(pid_t *p, float meas, float meas_rate, float dt);

float pid_output(const pid_t *p);
float pid_setpoint(const pid_t *p);
float pid_integral(const pid_t *p);

#endif /* PID_H */
