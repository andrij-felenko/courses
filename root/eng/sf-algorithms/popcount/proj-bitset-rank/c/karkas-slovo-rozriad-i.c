static inline uint64_t bs_tail_mask(size_t n) {
    unsigned r = (unsigned)(n & 63);
    return r ? (((uint64_t)1 << r) - 1) : ~(uint64_t)0;
}

static inline void bs_flip(uint64_t *w, size_t n) {
    size_t nw = BS_WORDS(n), j;
    for (j = 0; j < nw; ++j) w[j] = ~w[j];
    if (nw) w[nw - 1] &= bs_tail_mask(n);
}
