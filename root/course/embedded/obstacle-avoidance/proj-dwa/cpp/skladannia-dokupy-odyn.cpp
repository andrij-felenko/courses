// Один такт DWA: поточна швидкість + кільце дальностей + напрям на ціль
// → пара (v, w) двигунам. Повертає 1, якщо пара знайдена; 0 — біда (див. нижче).
int dwa_tick(float v0, float w0, const float obst_dist[N_RAYS],
             float goal_ang, float *out_v, float *out_w)
{
    Window win = dynamic_window(v0, w0);          // 1) вікно Vd ∩ Vs

    Cand cand[N_V * N_W];
    int  n = 0;

    // 2) Перебір сітки пар у вікні + сирі оцінки + допустимість Va.
    float dv = (win.v_hi - win.v_lo) / (N_V - 1 > 0 ? N_V - 1 : 1);
    float dw = (win.w_hi - win.w_lo) / (N_W - 1 > 0 ? N_W - 1 : 1);

    for (int iv = 0; iv < N_V; iv++) {
        for (int iw = 0; iw < N_W; iw++) {
            Cand *c = &cand[n];
            c->v = win.v_lo + iv * dv;
            c->w = win.w_lo + iw * dw;
            score_raw(c, obst_dist, goal_ang);    // heading, dist, velocity, admissible
            n++;
        }
    }

    // 3) Нормувати, згладити, вибрати найкращу допустиму пару.
    int best = pick_best(cand, n);

    if (best < 0) {                               // жодної допустимої пари — БІДА
        *out_v = 0.0f;                            // безпечний дефолт: гальмувати
        *out_w = 0.0f;
        return 0;                                 // сигнал верхньому поверху
    }

    *out_v = cand[best].v;                        // переможець — прямо двигунам
    *out_w = cand[best].w;
    return 1;
}
