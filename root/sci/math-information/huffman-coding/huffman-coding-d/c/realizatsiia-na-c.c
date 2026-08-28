typedef struct { int16_t idx[2 * SYMS]; int n; node_t *nodes; } heap_t;

static void heap_push(heap_t *h, int16_t v) {
    int i = h->n++;
    h->idx[i] = v;
    while (i > 0) {                       /* просіювання вгору */
        int parent = (i - 1) / 2;
        if (h->nodes[h->idx[parent]].freq <= h->nodes[h->idx[i]].freq) break;
        int16_t t = h->idx[parent]; h->idx[parent] = h->idx[i]; h->idx[i] = t;
        i = parent;
    }
}

static int16_t heap_pop(heap_t *h) {
    int16_t top = h->idx[0];
    h->idx[0] = h->idx[--h->n];
    int i = 0;                            /* просіювання вниз */
    for (;;) {
        int l = 2 * i + 1, r = 2 * i + 2, m = i;
        if (l < h->n && h->nodes[h->idx[l]].freq < h->nodes[h->idx[m]].freq) m = l;
        if (r < h->n && h->nodes[h->idx[r]].freq < h->nodes[h->idx[m]].freq) m = r;
        if (m == i) break;
        int16_t t = h->idx[m]; h->idx[m] = h->idx[i]; h->idx[i] = t;
        i = m;
    }
    return top;
}
