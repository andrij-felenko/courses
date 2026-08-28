typedef struct { double phase_margin_deg, gain_margin_db, wc, w180; int ok; } margins_t;

static margins_t measure_margins(const loop_t *m,
                                 double w_lo, double w_hi, int N) {
    margins_t r = {0};
    double prev_w   = w_lo;
    double complex prev_L = L_of_w(m, prev_w);
    double prev_mag = cabs(prev_L);
    double raw_prev = carg(prev_L);            // сире carg ∈ (-π, π]
    double unw_prev = raw_prev;                // РОЗГОРНУТА (безперервна) фаза
    int found_wc = 0, found_w180 = 0;

    for (int i = 1; i <= N; ++i) {
        double w   = w_lo * pow(w_hi / w_lo, (double)i / N);  // лог-крок
        double complex L = L_of_w(m, w);
        double mag = cabs(L);
        double raw = carg(L);

        // розгортка фази: прибираємо стрибки ±2π між сусідніми точками,
        // бо carg «перескакує» на межі −π/π, а нам треба безперервну фазу
        double d = raw - raw_prev;
        if (d >  M_PI) d -= 2.0 * M_PI;
        if (d < -M_PI) d += 2.0 * M_PI;
        double unw = unw_prev + d;

        // 1) кросовер підсилення: |L| перетнув 1 згори вниз → запас по фазі
        if (!found_wc && prev_mag >= 1.0 && mag < 1.0) {
            double t = (1.0 - prev_mag) / (mag - prev_mag);      // де саме mag=1
            r.wc = prev_w * pow(w / prev_w, t);
            double ph_wc = unw_prev + t * (unw - unw_prev);      // фаза в тій точці
            r.phase_margin_deg = 180.0 + ph_wc * 180.0 / M_PI;
            found_wc = 1;
        }
        // 2) частота −180°: РОЗГОРНУТА фаза перетнула −π → запас по підсиленню
        if (!found_w180 && unw_prev >= -M_PI && unw < -M_PI) {
            double t = (-M_PI - unw_prev) / (unw - unw_prev);
            r.w180 = prev_w * pow(w / prev_w, t);
            double gain_at_180 = cabs(L_of_w(m, r.w180));
            r.gain_margin_db = -20.0 * log10(gain_at_180);
            found_w180 = 1;
        }
        prev_w = w; prev_mag = mag; raw_prev = raw; unw_prev = unw;
    }
    r.ok = found_wc;          // без кросовера запас по фазі не визначений
    return r;
}
