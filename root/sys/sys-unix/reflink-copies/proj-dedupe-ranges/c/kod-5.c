static uint32_t run_len(const struct filerec *a, uint32_t ai,
                        const struct filerec *b, uint32_t bi)
{
    uint32_t k = 0;
    while (ai + k < a->nwin && bi + k < b->nwin &&
           a->h[ai + k] != 0 && a->h[ai + k] == b->h[bi + k])
        k++;
    return k;
}

static int keycmp(const void *A, const void *B)
{
    const struct key *a = A, *b = B;
    if (a->h != b->h) return a->h < b->h ? -1 : 1;
    if (a->f != b->f) return a->f < b->f ? -1 : 1;
    return a->w < b->w ? -1 : (a->w > b->w);
}

static int destcmp(const void *A, const void *B)   /* довші збіги спершу */
{
    uint32_t a = ((const struct dest *)A)->run, b = ((const struct dest *)B)->run;
    return a > b ? -1 : (a < b);
}

static void do_group(struct key *g, size_t n)
{
    struct filerec *src = &fr[g[0].f];
    uint32_t sw = g[0].w;

    struct dest *d = malloc(n * sizeof *d);
    if (!d) { fprintf(stderr, "бракує пам'яті\n"); exit(1); }

    size_t nd = 0;
    for (size_t i = 1; i < n; i++) {
        if (g[i].f == g[0].f) continue;              /* той самий inode */
        struct filerec *dst = &fr[g[i].f];
        if (dst->merged[g[i].w]) continue;           /* уже злите       */
        uint32_t r = run_len(src, sw, dst, g[i].w);
        if (r == 0) continue;
        d[nd].f = g[i].f; d[nd].w = g[i].w; d[nd].run = r;
        nd++;
    }

    qsort(d, nd, sizeof *d, destcmp);
    for (size_t i = 0; i < nd; ) {                   /* пачка = однакова довжина */
        size_t j = i;
        while (j < nd && d[j].run == d[i].run && j - i < max_dest) j++;
        send_batch(src, sw, d + i, j - i, d[i].run);
        i = j;
    }
    free(d);
}
