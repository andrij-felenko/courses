// зіставити весь набір A з набором B пробою відношення.
// out[] має вмістити A->count елементів; повертає кількість прийнятих пар.
// (пари з train == -1 у out теж лишаються — щоб зберегти відповідність за query.)
int orb_match_all(const orb_set_t *A, const orb_set_t *B,
                  float ratio, orb_match_t *out) {
    int accepted = 0;
    for (int i = 0; i < A->count; ++i) {
        out[i].query = i;
        out[i].train = -1;
        out[i].dist  = 257;

        if (B->count == 0)                       // порожній набір — нема з чим в'язати
            continue;

        int best, second;
        int j = orb_two_best(&A->d[i], B, &best, &second);
        if (j >= 0 && orb_pass_ratio(best, second, ratio)) {
            out[i].train = j;
            out[i].dist  = best;
            ++accepted;
        }
    }
    return accepted;
}
