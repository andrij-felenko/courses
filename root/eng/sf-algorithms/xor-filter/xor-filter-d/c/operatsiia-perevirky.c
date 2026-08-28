bool xor_contains(const xor_filter_t *filter, uint64_t key) {
    uint32_t h0 = reduce(hash_a(key, filter->seed), filter->block_len);
    uint32_t h1 = filter->block_len + reduce(hash_b(key, filter->seed), filter->block_len);
    uint32_t h2 = 2 * filter->block_len + reduce(hash_c(key, filter->seed), filter->block_len);

    uint8_t fp = compute_fingerprint(key, filter->seed);
    uint8_t combined = filter->B[h0] ^ filter->B[h1] ^ filter->B[h2];

    return (combined == fp);
}
