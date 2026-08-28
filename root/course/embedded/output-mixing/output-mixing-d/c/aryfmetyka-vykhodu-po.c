typedef struct { int min_us, trim_us, max_us; bool rev; } out_cfg;

int scaled_to_pwm(float v, const out_cfg *c) {
    // 1) реверс над нормованим значенням
    if (c->rev) v = -v;

    // 2) двобічний масштаб навколо тримa
    float pwm;
    if (v >= 0.0f) pwm = c->trim_us + v * (c->max_us  - c->trim_us);
    else           pwm = c->trim_us + v * (c->trim_us - c->min_us);

    // 3) затиск у межі
    if (pwm < c->min_us) pwm = c->min_us;
    if (pwm > c->max_us) pwm = c->max_us;
    return (int)(pwm + 0.5f);
}
