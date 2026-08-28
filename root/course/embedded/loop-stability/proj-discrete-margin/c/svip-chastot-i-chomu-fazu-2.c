#define NW 400                         /* точок свіпу; 400 на 5 декад = 80/декаду */

typedef struct {
    double w[NW];        /* частоти, рад/с            */
    double mag_db[NW];   /* |L| у дБ                  */
    double ph_deg[NW];   /* фаза, градуси (розгорнута) */
} sweep_t;

static void run_sweep(const loop_t *L, double w_lo, double w_hi, sweep_t *s) {
    log_sweep(w_lo, w_hi, NW, s->w);
    double ph_rad[NW];
    for (int i = 0; i < NW; ++i) {
        cplx Lw = loop_L(L, s->w[i]);
        double m = c_abs(Lw);
        s->mag_db[i] = 20.0 * log10(m);     /* дБ: 0 дБ = підсилення 1 */
        ph_rad[i] = c_arg(Lw);              /* сира фаза, (−π, π]        */
    }
    unwrap_phase(ph_rad, NW);               /* робимо криву неперервною  */
    for (int i = 0; i < NW; ++i)
        s->ph_deg[i] = ph_rad[i] * 180.0 / M_PI;
}
