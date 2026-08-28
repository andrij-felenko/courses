typedef struct { const uint8_t *p; size_t left; bool bad; } rd_t;

static bool take(rd_t *r, size_t n)          /* єдине місце перевірки меж */
{
    if (r->bad || r->left < n) { r->bad = true; return false; }
    return true;
}

static uint16_t rd_u16(rd_t *r)
{
    if (!take(r, 2)) return 0;
    uint16_t v = (uint16_t)(((uint16_t)r->p[0] << 8) | r->p[1]);
    r->p += 2; r->left -= 2;
    return v;
}
