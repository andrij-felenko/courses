/* Повертає розмір стиснутого; out має бути достатньо великий. */
size_t huff_compress(const uint8_t *in, size_t n, uint8_t *out, size_t out_cap) {
    uint32_t freq[SYMS] = {0};
    for (size_t i = 0; i < n; i++) freq[in[i]]++;

    uint8_t len[SYMS] = {0};
    if (n > 0) {
        node_t nodes[2 * SYMS];
        int16_t root = huff_build(nodes, freq);
        collect_lengths(nodes, root, 0, len);
    }
    code_t code[SYMS];
    canonical_codes(len, code);

    /* заголовок: 4 байти довжини потоку + 256 байтів довжин кодів */
    size_t p = 0;
    out[p++] = (uint8_t)(n);       out[p++] = (uint8_t)(n >> 8);
    out[p++] = (uint8_t)(n >> 16); out[p++] = (uint8_t)(n >> 24);
    memcpy(out + p, len, SYMS); p += SYMS;

    bitw_t w; bw_init(&w, out + p, out_cap - p);
    for (size_t i = 0; i < n; i++)
        bw_put(&w, code[in[i]].bits, code[in[i]].len);
    bw_flush(&w);
    return p + w.len;
}
