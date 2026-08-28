#define SYMS 256
#define MAXLEN 32

typedef struct {
    uint32_t freq;
    int16_t  left, right, symbol;
} node_t;

/* huff_build з купою — як у докладному розборі; повертає індекс кореня */
static int16_t huff_build(node_t *nodes, const uint32_t *freq);

static void collect_lengths(const node_t *nodes, int16_t i, int depth, uint8_t *len) {
    if (i < 0) return;                          /* немає дитини: правий бік обгортки єдиного символу */
    if (nodes[i].symbol >= 0) {                 /* листок */
        len[nodes[i].symbol] = (uint8_t)depth;  /* глибина листка = довжина його коду */
        return;
    }
    collect_lengths(nodes, nodes[i].left,  depth + 1, len);
    collect_lengths(nodes, nodes[i].right, depth + 1, len);
}
