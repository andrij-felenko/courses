float pid_step(PID *c, float setpoint, float meas, float dt)
{
    float e = setpoint - meas;                       /* помилка                      */

    /* I: накопичуємо й ОДРАЗУ затискаємо (антивіндап) */
    c->integral += e * dt;
    c->integral = clampf(c->integral, c->i_min, c->i_max);

    /* D: від виміру (не від помилки) → нема поштовху на зміну завдання */
    float deriv = (c->meas_prev - meas) / dt;        /* = −d(meas)/dt                */
    /* однополюсний ФНЧ на похідну: гасить шумові сплески */
    float a = dt / (dt + c->tau);                    /* 0 < a ≤ 1                    */
    c->deriv_f += (deriv - c->deriv_f) * a;

    /* сума трьох складових */
    float u = c->kp * e + c->ki * c->integral + c->kd * c->deriv_f;

    /* межі виконавчого органу */
    u = clampf(u, c->u_min, c->u_max);

    c->meas_prev = meas;                             /* запам'ятати для наступного   */
    return u;
}

/* скидання стану — викликати при зброєнні/зльоті, перш ніж контур піде в роботу */
void pid_reset(PID *c, float meas)
{
    c->integral = 0.0f;
    c->meas_prev = meas;        /* щоб перша похідна була 0, а не сплеск */
    c->deriv_f = 0.0f;
}
