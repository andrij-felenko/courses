struct pi_tuple {              /* у ядрі це struct t10_pi_tuple: __be16, __be16, __be32 */
    uint8_t guard[2];
    uint8_t app[2];
    uint8_t ref[4];
};

static uint16_t be16(const uint8_t *p) { return (uint16_t)(p[0] << 8 | p[1]); }
static uint32_t be32(const uint8_t *p)
{
    return (uint32_t)p[0] << 24 | (uint32_t)p[1] << 16 | (uint32_t)p[2] << 8 | p[3];
}
