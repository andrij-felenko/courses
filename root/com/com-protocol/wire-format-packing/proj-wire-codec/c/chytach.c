typedef struct {
    const uint8_t *p;
    const uint8_t *end;
    bool           bad;
} rd_t;

static void rd_init(rd_t *r, const uint8_t *buf, size_t n)
{
    r->p = buf; r->end = buf + n; r->bad = false;
}

static const uint8_t *rd_take(rd_t *r, size_t n)
{
    if (r->bad || (size_t)(r->end - r->p) < n) { r->bad = true; return NULL; }
    const uint8_t *at = r->p;
    r->p += n;
    return at;
}

static uint8_t rd_u8(rd_t *r)
{
    const uint8_t *b = rd_take(r, 1);
    return b ? b[0] : 0;
}

static uint16_t rd_u16(rd_t *r)
{
    const uint8_t *b = rd_take(r, 2);
    if (!b) return 0;
    return (uint16_t)(((uint32_t)b[0] << 8) | (uint32_t)b[1]);
}

static uint32_t rd_u32(rd_t *r)
{
    const uint8_t *b = rd_take(r, 4);
    if (!b) return 0;
    return ((uint32_t)b[0] << 24) | ((uint32_t)b[1] << 16)
         | ((uint32_t)b[2] <<  8) | ((uint32_t)b[3]);
}

static uint64_t rd_u64(rd_t *r)
{
    const uint8_t *b = rd_take(r, 8);
    if (!b) return 0;
    uint64_t v = 0;
    for (int i = 0; i < 8; i++) v = (v << 8) | b[i];
    return v;
}

static int32_t rd_i32(rd_t *r)
{
    uint32_t u = rd_u32(r);
    int32_t  v;
    memcpy(&v, &u, sizeof v);    /* ті самі біти, без залежності від редакції стандарту */
    return v;
}

static float rd_f32(rd_t *r)
{
    uint32_t u = rd_u32(r);
    float f;
    memcpy(&f, &u, sizeof f);
    return f;
}

/* Рядок віддаємо ПОКАЖЧИКОМ усередину буфера: нічого не копіюємо й не виділяємо.
   Це не C-рядок — завершального нуля в ньому нема. */
static bool rd_str(rd_t *r, const uint8_t **out, size_t *out_n)
{
    size_t n = rd_u8(r);
    const uint8_t *b = rd_take(r, n);
    *out = b; *out_n = b ? n : 0;
    return b != NULL;
}
