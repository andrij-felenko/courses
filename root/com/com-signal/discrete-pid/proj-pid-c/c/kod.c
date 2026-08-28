#include <stdint.h>

typedef struct {
    /* параметри (задаємо при ініціалізації) */
    float kp, ki, kd;        /* коефіцієнти П, І, Д                       */
    float tau;               /* стала фільтра похідної, с (≈ 1/(2πfc))    */
    float i_min, i_max;      /* межі інтеграла (антивіндап)               */
    float u_min, u_max;      /* межі виходу (фізичні межі виконавчого)    */
    /* стан (живе між тактами) */
    float integral;          /* накопичений інтеграл                      */
    float meas_prev;         /* вимір на попередньому такті               */
    float deriv_f;           /* відфільтрована похідна                    */
} PID;

void pid_init(PID *c, float kp, float ki, float kd, float tau,
              float i_min, float i_max, float u_min, float u_max)
{
    c->kp = kp;  c->ki = ki;  c->kd = kd;  c->tau = tau;
    c->i_min = i_min;  c->i_max = i_max;
    c->u_min = u_min;  c->u_max = u_max;
    c->integral = 0.0f;  c->meas_prev = 0.0f;  c->deriv_f = 0.0f;
}

static inline float clampf(float x, float lo, float hi)
{
    if (x < lo) return lo;
    if (x > hi) return hi;
    return x;
}
