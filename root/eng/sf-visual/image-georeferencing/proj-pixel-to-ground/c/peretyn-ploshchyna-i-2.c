typedef struct {
    const double *h;      /* h[i*ne + j] — метри над еліпсоїдом; i на північ, j на схід */
    int    nn, ne;
    double step;          /* крок сітки, метри */
    double n0, e0;        /* місцеві координати вузла [0][0], метри */
} Grid;

static int grid_height(const Grid *g, double n, double e, double *h)
{
    double fi = (n - g->n0)/g->step, fj = (e - g->e0)/g->step;
    int i = (int)floor(fi), j = (int)floor(fj);
    if (i < 0 || j < 0 || i >= g->nn - 1 || j >= g->ne - 1) return 0;
    double a = fi - i, b = fj - j;
    const double *r0 = g->h + i*g->ne + j, *r1 = r0 + g->ne;
    *h = (1-a)*((1-b)*r0[0] + b*r0[1]) + a*((1-b)*r1[0] + b*r1[1]);
    return 1;
}

/* Наскільки промінь вище рельєфу в точці t. Додатне — ще летимо. */
static int gap(const Shot *s, const double p0[3], const double d[3],
               const Grid *g, double t, double *out)
{
    double h_ter, h_ray = s->h0 - (p0[2] + t*d[2]);
    if (!grid_height(g, p0[0] + t*d[0], p0[1] + t*d[1], &h_ter)) return 0;
    *out = h_ray - h_ter;
    return 1;
}
