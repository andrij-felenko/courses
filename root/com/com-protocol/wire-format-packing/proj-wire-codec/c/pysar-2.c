static void wr_u8(wr_t *w, uint8_t v)
{
    uint8_t *b = wr_take(w, 1);
    if (b) b[0] = v;
}

static void wr_u16(wr_t *w, uint16_t v)
{
    uint8_t *b = wr_take(w, 2);
    if (!b) return;
    b[0] = (uint8_t)(v >> 8);
    b[1] = (uint8_t)(v);
}

static void wr_u32(wr_t *w, uint32_t v)
{
    uint8_t *b = wr_take(w, 4);
    if (!b) return;
    b[0] = (uint8_t)(v >> 24);
    b[1] = (uint8_t)(v >> 16);
    b[2] = (uint8_t)(v >>  8);
    b[3] = (uint8_t)(v);
}

static void wr_u64(wr_t *w, uint64_t v)
{
    uint8_t *b = wr_take(w, 8);
    if (!b) return;
    for (int i = 0; i < 8; i++)
        b[i] = (uint8_t)(v >> (56 - 8 * i));
}

static void wr_i32(wr_t *w, int32_t v)
{
    wr_u32(w, (uint32_t)v);      /* зведення за модулем 2³² = доповняльний код */
}

static void wr_f32(wr_t *w, float f)
{
    uint32_t u;
    memcpy(&u, &f, sizeof u);    /* біти IEEE 754 як звичайне ціле */
    wr_u32(w, u);
}

/* Рядок: один байт довжини, далі стільки ж байтів UTF-8, без нуля в кінці. */
static void wr_str(wr_t *w, const char *s, size_t n)
{
    if (n > 255) { w->bad = true; return; }
    wr_u8(w, (uint8_t)n);
    uint8_t *b = wr_take(w, n);
    if (b && n) memcpy(b, s, n);
}
