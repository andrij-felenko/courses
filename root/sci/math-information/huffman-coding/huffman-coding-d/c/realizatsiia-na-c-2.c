/* Повертає індекс кореня. nodes[] заповнюється; nfree — лічильник вузлів. */
static int16_t huff_build(node_t *nodes, const uint32_t *freq) {
    heap_t h; h.n = 0; h.nodes = nodes;
    int nfree = 0;

    for (int s = 0; s < SYMS; s++) {           /* листки лише для наявних символів */
        if (freq[s] == 0) continue;
        nodes[nfree] = (node_t){ freq[s], -1, -1, (int16_t)s };
        heap_push(&h, (int16_t)nfree++);
    }
    if (h.n == 1) {                            /* окремий випадок: один символ */
        int16_t only = heap_pop(&h);
        nodes[nfree] = (node_t){ nodes[only].freq, only, -1, -1 };
        return (int16_t)nfree++;               /* дамо йому довжину коду 1 */
    }
    while (h.n > 1) {                          /* зливаємо два найрідші */
        int16_t a = heap_pop(&h);
        int16_t b = heap_pop(&h);
        nodes[nfree] = (node_t){ nodes[a].freq + nodes[b].freq, a, b, -1 };
        heap_push(&h, (int16_t)nfree++);
    }
    return heap_pop(&h);                        /* останній — корінь */
}
