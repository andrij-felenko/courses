typedef struct { uint32_t bits; uint8_t len; } code_t;   /* код до 32 біт */

static void huff_codes(const node_t *nodes, int16_t i,
                       uint32_t bits, uint8_t len, code_t *out) {
    if (nodes[i].symbol >= 0) {                 /* листок — записати код */
        out[nodes[i].symbol].bits = bits;
        out[nodes[i].symbol].len  = len ? len : 1;   /* корінь-листок → 1 біт */
        return;
    }
    huff_codes(nodes, nodes[i].left,  (bits << 1),     len + 1, out);  /* 0 */
    huff_codes(nodes, nodes[i].right, (bits << 1) | 1, len + 1, out);  /* 1 */
}
