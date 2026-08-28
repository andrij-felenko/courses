void fm_block(int16_t *out, uint32_t n,
              double f_carrier, double f_msg, double deviation) {
    static uint32_t ph_c = 0, ph_m = 0;
    uint32_t inc_m = phase_inc(f_msg);
    for (uint32_t i = 0; i < n; i++) {
        double m      = sine_at(ph_m) / 32767.0;          // −1..+1
        double f_inst = f_carrier + deviation * m;         // миттєва частота
        ph_c += phase_inc(f_inst);                         // інтегруємо фазу!
        out[i] = sine_at(ph_c);                            // амплітуда стала
        ph_m += inc_m;
    }
}
