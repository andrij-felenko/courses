void am_block(int16_t *out, uint32_t n,
              double f_carrier, double f_msg, double mu) {
    static uint32_t ph_c = 0, ph_m = 0;
    uint32_t inc_c = phase_inc(f_carrier);
    uint32_t inc_m = phase_inc(f_msg);
    for (uint32_t i = 0; i < n; i++) {
        double m   = sine_at(ph_m) / 32767.0;        // повідомлення, −1..+1
        double env = 1.0 + mu * m;                    // огинаюча
        double s   = env * (sine_at(ph_c) / 32767.0); // несуча × огинаюча
        // діапазон env — [1−μ .. 1+μ]; нормуємо під ЦАП
        out[i] = (int16_t)lround(32767.0 * s / (1.0 + mu));
        ph_c += inc_c;
        ph_m += inc_m;
    }
}
