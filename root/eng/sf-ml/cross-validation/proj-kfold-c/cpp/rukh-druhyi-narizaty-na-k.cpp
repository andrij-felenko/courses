/* Розмір блоку f при поділі n на k з роздачею залишку першим блокам. */
static int fold_size(int n, int k, int f) {
    return n / k + (f < n % k ? 1 : 0);   /* перші (n%k) блоків — на 1 більші */
}

/* Початок (offset у order[]) блоку f: сума розмірів блоків 0..f-1. */
static int fold_start(int n, int k, int f) {
    int base = n / k, r = n % k;
    return f * base + (f < r ? f : r);    /* +по одному за кожен «довгий» блок до f */
}
