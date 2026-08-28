/* Силу кожної пари лічимо раз; +s тілу i, −s тілу j. */
void pair_forces(int n, const double *x, double *F, double k, double d0) {
    for (int i = 0; i < n; i++) F[i] = 0.0;
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++) {        /* кожна пара раз: i < j */
            double dx = x[i] - x[j];
            double r  = fabs(dx);
            if (r > 0.0 && r < d0) {             /* торкаються? */
                double s = k * (d0 - r) * (dx / r);  /* сила на i */
                F[i] += s;                        /* дія */
                F[j] -= s;                        /* протидія — те саме s */
            }
        }
}
