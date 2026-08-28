// Розрахунок лінеаризованої температури (°C)
double baro_compensate_temperature(const BaroCalibData *c, uint32_t uncomp_temp) {
    double dt = (double)uncomp_temp - c->t1;
    double t_lin = (dt * c->t2) + (dt * dt * c->t3);
    return t_lin;
}

// Повний розрахунок компенсованого тиску (Паскалі)
double baro_compensate_pressure(const BaroCalibData *c, uint32_t uncomp_press, double t_lin) {
    double t2 = t_lin * t_lin;
    double t3 = t2 * t_lin;
    double p_raw = (double)uncomp_press;
    double p2 = p_raw * p_raw;
    double p3 = p2 * p_raw;

    // Члени полінома: Offset(T), Sensitivity(T), NonLinearity(P, T)
    double offset = c->p1 + (c->p2 * t_lin) + (c->p3 * t2) + (c->p4 * t3);
    double sens   = c->p5 + (c->p6 * t_lin) + (c->p7 * t2) + (c->p8 * t3);
    double nonlin = (c->p9 + (c->p10 * t_lin)) * p2 + (c->p11 * p3);

    return offset + (sens * p_raw) + nonlin;
}
