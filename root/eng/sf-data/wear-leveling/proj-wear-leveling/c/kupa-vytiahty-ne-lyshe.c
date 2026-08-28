static void heap_swap(int i, int j) {
    uint16_t a = heap[i], b = heap[j];
    heap[i] = b; heap[j] = a;
    hpos[b] = i; hpos[a] = j;              // зворотні покажчики їдуть разом із блоками
}

static void sift_up(int i) {
    while (i > 0) {
        int par = (i - 1) / 2;
        if (ec[heap[par]] <= ec[heap[i]]) break;
        heap_swap(i, par);
        i = par;
    }
}

static void sift_down(int i) {
    for (;;) {
        int l = 2 * i + 1, r = l + 1, m = i;
        if (l < heap_n && ec[heap[l]] < ec[heap[m]]) m = l;
        if (r < heap_n && ec[heap[r]] < ec[heap[m]]) m = r;
        if (m == i) break;
        heap_swap(i, m);
        i = m;
    }
}

static void heap_push(uint16_t b) {
    heap[heap_n] = b;
    hpos[b] = heap_n;
    heap_n++;
    sift_up(heap_n - 1);
}
