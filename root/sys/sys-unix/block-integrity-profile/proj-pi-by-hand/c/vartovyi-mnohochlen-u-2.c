static uint16_t tab[256];

static void tab_init(void)
{
    for (unsigned i = 0; i < 256; i++) {
        uint8_t b = (uint8_t)i;
        tab[i] = crc_bit(&b, 1);
    }
}

static uint16_t crc_tab(const uint8_t *p, size_t n)
{
    uint16_t crc = 0;

    for (size_t i = 0; i < n; i++)
        crc = (uint16_t)(crc << 8) ^ tab[(crc >> 8) ^ p[i]];
    return crc;
}
