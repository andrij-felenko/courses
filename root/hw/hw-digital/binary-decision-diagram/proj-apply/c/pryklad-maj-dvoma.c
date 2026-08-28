static void mark(int u, char *seen) {
    if (seen[u]) return;
    seen[u] = 1;
    if (nodes[u].var != TERM) { mark(nodes[u].lo, seen); mark(nodes[u].hi, seen); }
}

int main(void) {
    bdd_init(64, 10, 10);                        /* пул + дві таблиці по 1024 слоти */
    int a = bdd_var(0), b = bdd_var(1), c = bdd_var(2);

    /* Спосіб 1 — прямо через ITE:  a ? (b+c) : (b·c) */
    int maj1 = ite(a, bdd_or(b, c), bdd_and(b, c));
    /* Спосіб 2 — сума добутків:  a·b + a·c + b·c */
    int maj2 = bdd_or(bdd_or(bdd_and(a, b), bdd_and(a, c)), bdd_and(b, c));

    printf("maj спосіб 1 (ITE)           = вузол #%d\n", maj1);
    printf("maj спосіб 2 (сума добутків) = вузол #%d\n", maj2);
    printf("тотожні? %s\n\n", maj1 == maj2 ? "так — той самий вузол" : "ні");

    char *seen = calloc(nnodes, 1);
    mark(maj1, seen);
    const char *nm = "abc";
    int internal = 0;
    for (int u = 2; u < nnodes; u++) internal += seen[u];
    printf("діаграма maj: %d внутрішніх вузли + 2 термінали\n", internal);
    for (int u = nnodes - 1; u >= 2; u--)
        if (seen[u])
            printf("  #%d  var %c  lo #%d  hi #%d\n",
                   u, nm[nodes[u].var], nodes[u].lo, nodes[u].hi);

    int parents = 0;
    for (int u = 2; u < nnodes; u++)
        if (seen[u] && (nodes[u].lo == c || nodes[u].hi == c)) parents++;
    printf("\nвузол #%d (c) має %d батьків — спільний, тож це граф\n", c, parents);
    return 0;
}
