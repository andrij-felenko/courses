// повна конфігурація контуру (викликати один раз при запуску)
void p_config(p_ctrl_t *c, float kp, float beta,
              float u_min, float u_max, float u_bias)
{
    c->kp     = kp;
    c->beta   = beta;
    c->u_min  = u_min;
    c->u_max  = u_max;
    c->u_bias = u_bias;
    p_reset(c);                 // привести діагностику до відомого стану
}

// «скидання» P: стану нема, тож лише чистимо діагностичні вікна
void p_reset(p_ctrl_t *c)
{
    c->last_u    = 0.0f;
    c->saturated = false;
    // ЖОДНОГО накопичувача обнуляти не треба — P безстанний.
}
