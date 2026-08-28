static void cfg_w32(uint8_t b, uint8_t d, uint8_t f, uint16_t o, uint32_t v)
{
    *cfg_ptr(b, d, f, o) = v;                          /* слово лягає цілком */
}

static void cfg_w16(uint8_t b, uint8_t d, uint8_t f, uint16_t o, uint16_t v)
{
    volatile uint32_t *p = cfg_ptr(b, d, f, o);
    unsigned sh = (o & 2) * 8;
    *p = (*p & ~(0xFFFFu << sh)) | ((uint32_t)v << sh); /* читання-зміна-запис */
}

static void cfg_w8(uint8_t b, uint8_t d, uint8_t f, uint16_t o, uint8_t v)
{
    volatile uint32_t *p = cfg_ptr(b, d, f, o);
    unsigned sh = (o & 3) * 8;
    *p = (*p & ~(0xFFu << sh)) | ((uint32_t)v << sh);
}
