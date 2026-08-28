void welford_merge(welford_t *dst, const welford_t *src) {
    if (!dst || !src || src->count == 0) return;
    if (dst->count == 0) {
        *dst = *src;
        return;
    }

    uint64_t total_count = dst->count + src->count;
    double delta = src->mean - dst->mean;
    double n_a = (double)dst->count;
    double n_b = (double)src->count;
    double n_ab = (double)total_count;

    dst->mean += delta * (n_b / n_ab);
    dst->M2 += src->M2 + delta * delta * (n_a * n_b / n_ab);
    dst->count = total_count;
}
