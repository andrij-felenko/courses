/* Розгортка фази на місці: прибирає стрибки ±360°, роблячи криву неперервною */
static void unwrap_phase(double *ph, int N) {
    double corr = 0.0;                 /* накопичена поправка, рад */
    for (int i = 1; i < N; ++i) {
        double d = (ph[i] + corr) - ph[i - 1];
        if (d >  M_PI) corr -= 2.0 * M_PI;   /* стрибок угору > 180° → тягнемо вниз */
        else if (d < -M_PI) corr += 2.0 * M_PI;
        ph[i] += corr;
    }
}
