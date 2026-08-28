const uint8_t N = 5;                // усереднюємо по 5 останніх інтервалів
uint32_t g_intervals[N] = {0};
uint8_t  g_idx = 0;
uint32_t g_prevBeat = 0;
bool     g_haveFirst = false;

// Викликати в мить кожного зарахованого удару (now — його час).
int computeBPM(uint32_t now) {
    if (!g_haveFirst) {             // перший удар: інтервалу ще нема
        g_prevBeat = now;
        g_haveFirst = true;
        return 0;                   // ще нема що рахувати
    }
    uint32_t beatMs = now - g_prevBeat;
    g_prevBeat = now;

    // Відкидаємо явно хибні інтервали (поза людським діапазоном 30..240 уд/хв).
    if (beatMs < 250 || beatMs > 2000) return -1;   // -1 = «підозрілий удар, пропускаємо»

    g_intervals[g_idx] = beatMs;
    g_idx = (g_idx + 1) % N;

    // Середній інтервал по заповнених комірках → BPM.
    uint32_t sum = 0; uint8_t cnt = 0;
    for (uint8_t i = 0; i < N; i++)
        if (g_intervals[i] > 0) { sum += g_intervals[i]; cnt++; }
    if (cnt == 0) return 0;
    return 60000UL / (sum / cnt);
}
