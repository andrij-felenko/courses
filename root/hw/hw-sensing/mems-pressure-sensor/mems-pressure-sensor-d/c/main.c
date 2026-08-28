// Поліноміальна компенсація 24-бітного барометра
double compensate_pressure_pa(uint32_t raw_p, uint32_t raw_t, const BaroCalib *c, double *out_temp_c) {
    // 1. Температурна компенсація
    double dt = (double)raw_t - c->t1;
    double t_lin = (dt * c->t2) + (dt * dt * c->t3);
    if (out_temp_c) *out_temp_c = t_lin;

    // 2. Складові полінома тиску
    double t2 = t_lin * t_lin;
    double t3 = t2 * t_lin;
    double p_raw = (double)raw_p;
    double p2 = p_raw * p_raw;
    double p3 = p2 * p_raw;

    double offset = c->p1 + (c->p2 * t_lin) + (c->p3 * t2) + (c->p4 * t3);
    double sens   = c->p5 + (c->p6 * t_lin) + (c->p7 * t2) + (c->p8 * t3);
    double nonlin = (c->p9 + (c->p10 * t_lin)) * p2 + (c->p11 * p3);

    return offset + (sens * p_raw) + nonlin;
}
