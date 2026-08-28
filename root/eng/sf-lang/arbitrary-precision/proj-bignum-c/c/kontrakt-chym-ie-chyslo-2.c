static void big_trim(big *x) {
    while (x->n > 0 && x->d[x->n - 1] == 0) x->n--;
    if (x->n == 0) x->neg = 0;
}

static void big_reserve(big *x, size_t need) {
    if (x->cap >= need) return;
    size_t cap = x->cap ? x->cap : 4;
    while (cap < need) cap *= 2;
    limb *p = realloc(x->d, cap * sizeof *p);
    if (!p) abort();                 // у справжній бібліотеці — код помилки
    x->d = p;
    x->cap = cap;
}
