/* Пошук індексу повідомлення за алгоритмом CHD за O(1) на C99 */
uint32_t emb_mphf_lookup(const uint8_t *g_table, uint32_t r, uint32_t n, const char *key) {
    uint32_t h0 = emb_murmur3(key, SEED_0) % r;
    uint32_t d  = g_table[h0]; /* Зчитування коефіцієнта зміщення */
    
    uint32_t h1 = emb_murmur3(key, SEED_1) % n;
    if (d == 0) return h1;
    
    uint32_t h2 = emb_murmur3(key, SEED_2) % n;
    return (h1 + d * h2) % n;
}
