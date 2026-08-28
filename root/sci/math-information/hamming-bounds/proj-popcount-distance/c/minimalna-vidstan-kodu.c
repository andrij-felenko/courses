// d_min малого коду: перебір усіх пар. Слова — у масиві code[0..n-1].
int min_distance(const uint32_t *code, int n) {
    int best = INT_MAX;
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++) {      // кожну пару — один раз
            int d = hamming_distance(code[i], code[j]);
            if (d < best) best = d;
        }
    return best;                                 // n < 2 → лишиться INT_MAX
}
