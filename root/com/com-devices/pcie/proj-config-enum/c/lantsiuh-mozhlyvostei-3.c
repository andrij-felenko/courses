static void walk_ext_caps(uint8_t b, uint8_t d, uint8_t f)
{
    uint16_t off = 0x100;
    for (int ttl = 48; off >= 0x100 && off < 0x1000 && ttl; ttl--) {
        uint32_t h = cfg_r32(b, d, f, off);
        if (h == 0 || h == 0xFFFFFFFFu)
            return;                                  /* розширених можливостей немає */

        printf("  ext %04x  версія %u  @ %03x\n",
               h & 0xFFFFu, (h >> 16) & 0xFu, (unsigned)off);

        off = (uint16_t)((h >> 20) & 0xFFCu);        /* біти 31:20 — наступний, вирівняний */
    }
}
