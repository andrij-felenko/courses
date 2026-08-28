// індекс найкращого дескриптора в B для заданого query;
// у *best_out / *second_out кладе дві найменші відстані Гаммінга.
static int orb_two_best(const orb_desc_t *query, const orb_set_t *B,
                        int *best_out, int *second_out) {
    int best = 257, second = 257, best_j = -1;   // 257 > будь-якої реальної відстані
    for (int j = 0; j < B->count; ++j) {
        int d = orb_hamming(query, &B->d[j]);
        if (d < best) {                          // новий рекорд: старий best з'їжджає в second
            second = best;
            best   = d;
            best_j = j;
        } else if (d < second) {                 // не рекорд, але кращий за другий
            second = d;
        }
    }
    if (best_out)   *best_out   = best;
    if (second_out) *second_out = second;
    return best_j;                               // -1, лише якщо B порожній
}
