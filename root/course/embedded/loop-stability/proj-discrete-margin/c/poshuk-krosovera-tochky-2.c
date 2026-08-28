static void find_gain_margin(const sweep_t *s, margins_t *m) {
    m->has_pc = 0;
    for (int i = 0; i + 1 < NW; ++i) {
        /* точка −180°: фаза падає з «> −180» у «< −180» */
        if (s->ph_deg[i] >= -180.0 && s->ph_deg[i + 1] < -180.0) {
            double mag = interp_at_crossing(s->w, s->ph_deg, s->mag_db, i, -180.0);
            m->w_pc = interp_at_crossing(s->w, s->ph_deg, s->w, i, -180.0);
            m->gm_db = 0.0 - mag;              /* наскільки |L| нижче 0 дБ */
            m->has_pc = 1;
            return;                            /* перший перетин −180°     */
        }
    }
}
