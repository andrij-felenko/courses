// Чи впирається регулятор у стелю саме зараз (після останнього кроку)?
// Порівнюємо необмежений вихід із межами — але u_unsat живе локально в
// pid_update. Тож зробимо крок, що ПОВЕРТАЄ і вихід, і прапорець насичення.
typedef struct {
    float u;            // обмежений вихід
    bool  saturated;    // чи вихід уперся в межу
} pid_out_t;

pid_out_t pid_update_ex(pid_t *p, float setpoint, float meas, float dt)
{
    // (тіло — те саме, що pid_update, лише додаємо детекцію насичення)
    pid_out_t out = { .u = 0.0f, .saturated = false };
    if (dt <= 0.0f) return out;

    if (!p->initialized) {
        p->meas_prev = meas; p->deriv_filt = 0.0f; p->initialized = true;
    }

    float e   = setpoint - meas;
    float e_p = p->b * setpoint - meas;

    float d_raw = -(meas - p->meas_prev) / dt;
    float tau_d = (p->Kp != 0.0f) ? (p->Kd / p->Kp) / p->N : 0.0f;
    float alpha = dt / (dt + tau_d);
    p->deriv_filt += alpha * (d_raw - p->deriv_filt);

    float integral_try = p->integral + p->Ki * e * dt;
    float u_unsat = p->Kp * e_p + integral_try + p->Kd * p->deriv_filt;

    float u = u_unsat;
    if (u > p->u_max) { u = p->u_max; out.saturated = true; }
    if (u < p->u_min) { u = p->u_min; out.saturated = true; }

    if (p->aw == AW_CLAMP) {
        bool push_high = (u_unsat > p->u_max) && (e > 0.0f);
        bool push_low  = (u_unsat < p->u_min) && (e < 0.0f);
        if (!push_high && !push_low) p->integral = integral_try;
    } else {
        p->integral += (p->Ki * e + p->Kaw * (u - u_unsat)) * dt;
    }

    p->meas_prev = meas;
    out.u = u;
    return out;
}
