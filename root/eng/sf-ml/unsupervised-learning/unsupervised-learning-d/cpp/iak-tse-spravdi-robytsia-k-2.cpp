void update_step(const Pt *pts, int N, Pt *cent, int K, const int *assign) {
    double sx[K], sy[K];  int cnt[K];
    for (int c = 0; c < K; c++) { sx[c] = sy[c] = 0.0; cnt[c] = 0; }

    for (int i = 0; i < N; i++) {      // зібрати суми по кожній групі
        int c = assign[i];
        sx[c] += pts[i].x;  sy[c] += pts[i].y;  cnt[c]++;
    }
    for (int c = 0; c < K; c++) {
        if (cnt[c] > 0) {              // центр = середнє своїх точок
            cent[c].x = sx[c] / cnt[c];
            cent[c].y = sy[c] / cnt[c];
        }
        // cnt[c] == 0 — «порожній» центр: нікого не притягнув, лишаємо на місці
    }
}
