/* синдром прийнятого слова = word mod g(x); 0 ⇒ помилки не видно */
static uint16_t syndrome(uint16_t word) { return poly_rem(word); }

static int weight(uint16_t v) {           /* вага Геммінга: скільки одиниць */
    int w = 0;
    while (v) { w += v & 1; v >>= 1; }
    return w;
}

static uint16_t rotl(uint16_t w) {        /* циклічний зсув уліво в N розрядах */
    uint16_t top = (w >> (N - 1)) & 1;    /* біт, що зіскакує зверху, — назад у молодший */
    return ((w << 1) | top) & ((1u << N) - 1);
}
static uint16_t rotr(uint16_t w) {        /* циклічний зсув управо в N розрядах */
    uint16_t bot = w & 1;                 /* молодший біт — наверх */
    return ((w >> 1) | (bot << (N - 1))) & ((1u << N) - 1);
}
