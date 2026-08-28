void big_mul(big *r, const big *a, const big *b) {
    if (a->n == 0 || b->n == 0) { r->n = 0; r->neg = 0; return; }
    size_t n = a->n + b->n;
    limb *t = malloc(n * sizeof *t);
    if (!t) abort();
    mul_basecase(t, a->d, a->n, b->d, b->n);
    free(r->d);                    // r міг бути тим самим об'єктом, що a чи b:
    r->d   = t;                    // до цього рядка ми дочитали все потрібне
    r->cap = n;
    r->neg = (a->neg != b->neg);
    r->n   = n - (t[n - 1] == 0);  // лімбів або n, або n−1 — третього не буває
}
