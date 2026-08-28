static uint64_t bar_size(uint8_t b, uint8_t d, uint8_t f, uint16_t off, int is64)
{
    uint16_t cmd = cfg_r16(b, d, f, 0x04);
    cfg_w16(b, d, f, 0x04, (uint16_t)(cmd & ~3u));   /* глушимо декодування: BAR зараз «поїде» */

    uint32_t lo = cfg_r32(b, d, f, off);
    uint32_t hi = is64 ? cfg_r32(b, d, f, (uint16_t)(off + 4)) : 0;

    cfg_w32(b, d, f, off, 0xFFFFFFFFu);
    uint64_t raw = cfg_r32(b, d, f, off) & ~0xFu;
    if (is64) {
        cfg_w32(b, d, f, (uint16_t)(off + 4), 0xFFFFFFFFu);
        raw |= (uint64_t)cfg_r32(b, d, f, (uint16_t)(off + 4)) << 32;
        cfg_w32(b, d, f, (uint16_t)(off + 4), hi);
    }
    cfg_w32(b, d, f, off, lo);                /* повертаємо як було */
    cfg_w16(b, d, f, 0x04, cmd);              /* і вмикаємо декодування назад */

    if (raw == 0)
        return 0;                             /* BAR не реалізований */

    uint64_t mask = is64 ? raw : (raw | 0xFFFFFFFF00000000ull);
    return ~mask + 1;                         /* молодший встановлений біт і є розмір */
}
