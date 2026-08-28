/* Результат аналізу: три числа + частоти, де вони живуть */
typedef struct {
    double pm_deg;      /* запас по фазі, градуси          */
    double gm_db;       /* запас по підсиленню, дБ         */
    double w_gc;        /* частота кросовера (gain xover)  */
    double w_pc;        /* частота фази −180° (phase xover) */
    int    has_gc;      /* чи знайдено кросовер            */
    int    has_pc;      /* чи знайдено точку −180°         */
} margins_t;

static void find_phase_margin(const sweep_t *s, margins_t *m) {
    m->has_gc = 0;
    for (int i = 0; i + 1 < NW; ++i) {
        /* кросовер: mag_db падає з «>0» у «<0» */
        if (s->mag_db[i] >= 0.0 && s->mag_db[i + 1] < 0.0) {
            double ph = interp_at_crossing(s->w, s->mag_db, s->ph_deg, i, 0.0);
            m->w_gc = interp_at_crossing(s->w, s->mag_db, s->w, i, 0.0);
            m->pm_deg = ph - (-180.0);         /* скільки фазі лишилось до −180° */
            m->has_gc = 1;
            return;                            /* перший (найнижчий) кросовер */
        }
    }
}
