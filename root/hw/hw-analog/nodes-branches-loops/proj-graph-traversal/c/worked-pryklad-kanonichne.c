int main(void) {
    Branch branches[] = {
        /* 0: V  */ { 2, 0 },     /* C–A */
        /* 1: R3 */ { 0, 2 },     /* A–C */
        /* 2: R1 */ { 0, 1 },     /* A–B */
        /* 3: R2 */ { 1, 2 },     /* B–C */
    };
    uint8_t N = 3, B = 4;

    for (uint8_t i = 0; i < B; ++i)
        add_edge(i, branches[i].a, branches[i].b);

    uint8_t seen = dfs(0);        /* старт із вузла A = 0 */

    /* seen    == 3  → граф зв'язний (охопив усі 3 вузли)
       n_tree  == N - 1   == 2 гілки в кістяковому дереві
       n_chords== B - N + 1 == 2 хорди, кожна замикає свій контур
       chord[0..1] → самі хорди (тут — R3 і R2) */
    if (seen != N || n_tree != N - 1 || n_chords != B - N + 1)
        return 1;                             /* топологія не збіглася */

    /* кожна хорда → свій фундаментальний контур */
    static const char *NAME[] = { "V", "R3", "R1", "R2" };
    for (uint8_t i = 0; i < n_chords; ++i) {
        uint8_t loop[MAX_N];
        uint8_t len = collect_loop(chord[i], branches, loop);
        printf("контур хорди %s:", NAME[chord[i]]);
        for (uint8_t j = 0; j < len; ++j) printf(" %s", NAME[loop[j]]);
        printf("\n");
    }
    return 0;
}
