typedef struct {
    const uint8_t *data;
    long  nbits;
    long  pos;
    int   bad;          /* біти скінчилися або поле безглузде */
} bits_t;

static void bits_init(bits_t *br, const uint8_t *data, long nbytes)
{
    br->data = data; br->nbits = nbytes * 8; br->pos = 0; br->bad = 0;
}

static unsigned u1(bits_t *br)
{
    if (br->pos >= br->nbits) { br->bad = 1; return 0; }
    unsigned v = (br->data[br->pos >> 3] >> (7 - (br->pos & 7))) & 1u;
    br->pos++;
    return v;
}

static uint32_t un(bits_t *br, int n)
{
    uint32_t v = 0;
    for (int i = 0; i < n; i++) v = (v << 1) | u1(br);
    return v;
}

/* ue(v): k нулів, одиничка, k бітів залишку → (2^k − 1) + залишок. */
static uint32_t ue(bits_t *br)
{
    int lead = 0;
    while (u1(br) == 0) {
        if (++lead > 31 || br->bad) { br->bad = 1; return 0; }
    }
    return lead ? ((1u << lead) - 1 + un(br, lead)) : 0;
}

/* se(v): те саме ue, розкладене в знак: 0→0, 1→+1, 2→−1, 3→+2, 4→−2 … */
static int32_t se(bits_t *br)
{
    uint32_t k = ue(br);
    int32_t  v = (int32_t)((k + 1) >> 1);
    return (k & 1) ? v : -v;
}
