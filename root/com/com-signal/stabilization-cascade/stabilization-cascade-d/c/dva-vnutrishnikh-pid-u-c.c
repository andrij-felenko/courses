typedef struct {
    float kp, ki, kd;          // коефіцієнти
    float integ;               // накопичений інтеграл (стан)
    float meas_prev;           // попередній вимір (стан, для D)
    float i_min, i_max;        // межі антивіндапу
    float out_min, out_max;    // межі виходу
} PID;

// один такт: ціль (setpoint), вимір (meas), крок часу dt
float pid_step(PID *p, float setpoint, float meas, float dt) {
    float e = setpoint - meas;                    // помилка
    p->integ += e * dt;                           // I: накопичуємо
    if (p->integ > p->i_max) p->integ = p->i_max; // антивіндап
    if (p->integ < p->i_min) p->integ = p->i_min;
    float deriv = (p->meas_prev - meas) / dt;     // D від ВИМІРУ (не від помилки)
    p->meas_prev = meas;
    float u = p->kp * e + p->ki * p->integ + p->kd * deriv;
    if (u > p->out_max) u = p->out_max;           // межі виконавчого органу
    if (u < p->out_min) u = p->out_min;
    return u;
}
