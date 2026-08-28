// Перехресна ентропія H(q, p) = −Σ qᵢ·ln(pᵢ).
// q — м'яка мітка вчителя, p — розподіл учня (обидва за тією самою T).
// eps підпирає ln, щоб ln(0) не дав −inf.
static float cross_entropy(const float *q, const float *p, int n) {
    const float eps = 1e-7f;
    float h = 0.0f;
    for (int i = 0; i < n; ++i)
        h -= q[i] * logf(fmaxf(p[i], eps));
    return h;
}
