// Прорідження шару за модулем: усе, що менше за поріг, — у нуль.
// w[]    — ваги шару (float), n штук
// mask[] — 1 = вага жива, 0 = викинута назавжди
void prune_by_magnitude(float *w, unsigned char *mask, int n, float thr) {
    for (int i = 0; i < n; i++) {
        if (fabsf(w[i]) < thr) {   // мала за модулем — баласт
            w[i]    = 0.0f;
            mask[i] = 0;           // позначаємо: сюди більше не вертатись
        }
    }
}
