// p_controller_fixed.c — один такт у Q16, захищений від переповнення
int32_t p_step_q(p_ctrl_q_t *c, int32_t setpoint, int32_t measure)
{
    // узагальнена помилка зі зважуванням завдання; beta_q у Q16, тож
    // beta_q*setpoint теж треба зсунути назад — робимо це через qmul_shift
    int32_t weighted_sp = qmul_shift(c->beta_q, setpoint);   // beta * r
    int32_t e = weighted_sp - measure;                       // узагальнена помилка

    int32_t u = qmul_shift(c->kp_q, e) + c->u_bias;          // Kp*e + bias

    c->last_u = u;
    c->saturated = false;
    if (u > c->u_max) { u = c->u_max; c->saturated = true; }
    if (u < c->u_min) { u = c->u_min; c->saturated = true; }
    return u;
}
