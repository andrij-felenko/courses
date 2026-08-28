// p, b — рядково-неперервні масиви n×n; ∇²p = b, Нейман на стінках.
// Ґаусс — Зайдель пише просто в p: нижні сусіди вже свіжі → удвічі швидша збіжність.
void poisson(double* p, const double* b, int n, double dx, double dy, int nit) {
    const double dx2 = dx*dx, dy2 = dy*dy, denom = 2.0 * (dx2 + dy2);
    auto at = [n](int j, int i) { return j * n + i; };
    for (int it = 0; it < nit; ++it) {
        for (int j = 1; j < n - 1; ++j)
            for (int i = 1; i < n - 1; ++i)
                p[at(j, i)] = ( (p[at(j, i+1)] + p[at(j, i-1)]) * dy2
                              + (p[at(j+1, i)] + p[at(j-1, i)]) * dx2
                              - b[at(j, i)] * dx2 * dy2 ) / denom;
        for (int j = 0; j < n; ++j) {              // Нейман: ∂p/∂n = 0
            p[at(j, 0)]   = p[at(j, 1)];
            p[at(j, n-1)] = p[at(j, n-2)];
        }
        for (int i = 0; i < n; ++i) {
            p[at(0, i)]   = p[at(1, i)];
            p[at(n-1, i)] = p[at(n-2, i)];
        }
        p[0] = 0.0;                                // закріпити відлік тиску
    }
}
