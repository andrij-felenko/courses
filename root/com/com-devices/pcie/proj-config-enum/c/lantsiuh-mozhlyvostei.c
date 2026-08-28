static uint8_t find_cap(uint8_t b, uint8_t d, uint8_t f, uint8_t id)
{
    if ((cfg_r16(b, d, f, 0x06) & 0x10u) == 0)
        return 0;                                    /* списку немає взагалі */

    uint8_t p = cfg_r8(b, d, f, 0x34) & 0xFCu;       /* два молодші біти — резерв */
    for (int ttl = 48; p >= 0x40 && ttl; ttl--) {    /* лічильник — від зациклення */
        if (cfg_r8(b, d, f, p) == id)
            return p;
        p = cfg_r8(b, d, f, (uint16_t)(p + 1)) & 0xFCu;
    }
    return 0;
}
