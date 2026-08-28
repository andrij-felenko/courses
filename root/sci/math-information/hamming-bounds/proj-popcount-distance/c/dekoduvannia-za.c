// Повертає індекс найближчого кодового слова; *out_d — його відстань.
int decode_nearest(const uint32_t *code, int n, uint32_t got, int *out_d) {
    int best_i = 0, best_d = INT_MAX;
    for (int i = 0; i < n; i++) {
        int d = hamming_distance(got, code[i]);
        if (d < best_d) { best_d = d; best_i = i; }   // ближчий — запам'ятати
    }
    if (out_d) *out_d = best_d;
    return best_i;
}
