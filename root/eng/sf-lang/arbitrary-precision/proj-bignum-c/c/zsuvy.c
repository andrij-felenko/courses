void big_shl(big *x, size_t k) {
    if (x->n == 0 || k == 0) return;
    size_t words = k / LIMB_BITS, bits = k % LIMB_BITS;
    size_t n = x->n + words + (bits != 0);
    big_reserve(x, n);
    limb *d = x->d;                       // тільки ПІСЛЯ можливого realloc
    if (bits) {
        d[x->n + words] = d[x->n - 1] >> (LIMB_BITS - bits);
        for (size_t i = x->n - 1; i > 0; i--)
            d[i + words] = (d[i] << bits) | (d[i - 1] >> (LIMB_BITS - bits));
        d[words] = d[0] << bits;
    } else {
        for (size_t i = x->n; i-- > 0; ) d[i + words] = d[i];
    }
    memset(d, 0, words * sizeof *d);
    x->n = n;
    big_trim(x);
}

void big_shr(big *x, size_t k) {
    size_t words = k / LIMB_BITS, bits = k % LIMB_BITS;
    if (words >= x->n) { x->n = 0; x->neg = 0; return; }
    limb  *d = x->d;
    size_t n = x->n - words;
    if (bits) {
        for (size_t i = 0; i + 1 < n; i++)
            d[i] = (d[i + words] >> bits) | (d[i + words + 1] << (LIMB_BITS - bits));
        d[n - 1] = d[x->n - 1] >> bits;
    } else {
        memmove(d, d + words, n * sizeof *d);
    }
    x->n = n;
    big_trim(x);
}
