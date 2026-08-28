// Передбачення виходу інвертувального суматора на N входів.
// rfb — резистор зворотного зв'язку (Ом); rin[i] — вхідні резистори (Ом);
// uin[i] — вхідні напруги (В). Повертає Uвих (В), знак уже з мінусом.
float summing_output(float rfb, const float *rin, const float *uin, int n)
{
    float acc = 0.0f;
    for (int i = 0; i < n; ++i)
        acc += uin[i] / rin[i];   // струм гілки: Iₖ = Uₖ / Rₖ
    return -rfb * acc;            // Uвих = −Rзз · Σ (Uₖ/Rₖ)
}
