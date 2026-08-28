static inline size_t bs_and_count(const uint64_t *a, const uint64_t *b, size_t nw) {
    size_t n0 = 0, n1 = 0, n2 = 0, n3 = 0, i = 0;
    for (; i + 4 <= nw; i += 4) {
        n0 += (size_t)pc64(a[i]     & b[i]);
        n1 += (size_t)pc64(a[i + 1] & b[i + 1]);
        n2 += (size_t)pc64(a[i + 2] & b[i + 2]);
        n3 += (size_t)pc64(a[i + 3] & b[i + 3]);
    }
    for (; i < nw; ++i) n0 += (size_t)pc64(a[i] & b[i]);
    return n0 + n1 + n2 + n3;
}
