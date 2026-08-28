/* Векторний запас: найкоротша відстань годографа L(w) до критичної точки −1 */
static double vector_margin(const loop_t *L, const sweep_t *s) {
    double best = 1e300;
    for (int i = 0; i < NW; ++i) {
        cplx Lw = loop_L(L, s->w[i]);
        /* відстань від L до (−1,0) = |L − (−1)| = |L + 1| */
        double dre = Lw.re + 1.0;
        double dim = Lw.im;
        double dist = sqrt(dre * dre + dim * dim);
        if (dist < best) best = dist;
    }
    return best;
}
