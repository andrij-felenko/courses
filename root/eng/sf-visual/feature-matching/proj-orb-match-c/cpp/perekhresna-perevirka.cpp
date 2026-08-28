// перехресна перевірка: лишити тільки взаємні пари.
// fwd[] — результат orb_match_all(A, B, ...); out[] вміщує A->count пар.
// Повертає кількість взаємних пар.
int orb_cross_check(const orb_set_t *A, const orb_set_t *B,
                    const orb_match_t *fwd, orb_match_t *out) {
    int kept = 0;
    for (int i = 0; i < A->count; ++i) {
        out[i].query = i;
        out[i].train = -1;
        out[i].dist  = 257;

        int j = fwd[i].train;                    // кого A[i] обрала вперед
        if (j < 0) continue;                     // вперед пари не було

        // кого B[j] обирає назад у A — тут БЕЗ проби відношення, лише найкращий
        int back_best, back_second;
        int back_i = orb_two_best(&B->d[j], A, &back_best, &back_second);

        if (back_i == i) {                       // взаємний вибір!
            out[i].train = j;
            out[i].dist  = fwd[i].dist;
            ++kept;
        }
    }
    return kept;
}
