static inline size_t bs_count(const uint64_t *w, size_t nw) {
    size_t n0 = 0, n1 = 0, n2 = 0, n3 = 0, i = 0;
    for (; i + 4 <= nw; i += 4) {
        n0 += (size_t)pc64(w[i]);
        n1 += (size_t)pc64(w[i + 1]);
        n2 += (size_t)pc64(w[i + 2]);
        n3 += (size_t)pc64(w[i + 3]);
    }
    for (; i < nw; ++i) n0 += (size_t)pc64(w[i]);
    return n0 + n1 + n2 + n3;
}
