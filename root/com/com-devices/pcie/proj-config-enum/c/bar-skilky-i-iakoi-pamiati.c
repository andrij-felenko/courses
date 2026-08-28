static void decode_bars(uint8_t b, uint8_t d, uint8_t f, int count)
{
    for (int i = 0; i < count; i++) {
        uint16_t off = (uint16_t)(0x10 + 4 * i);
        uint32_t lo  = cfg_r32(b, d, f, off);
        if (lo == 0)
            continue;                                  /* BAR не реалізований */

        if (lo & 1u) {                                 /* простір вводу-виводу */
            printf("  BAR%d  I/O   0x%04x\n", i, lo & ~3u);
            continue;
        }

        int      is64 = ((lo >> 1) & 3u) == 2u;
        int      pref = (lo >> 3) & 1u;
        uint64_t base = lo & ~0xFu;
        int      idx  = i;

        if (is64) {
            base |= (uint64_t)cfg_r32(b, d, f, (uint16_t)(off + 4)) << 32;
            i++;                                       /* верхнє слово — частина ЦЬОГО ж BAR-а */
        }

        printf("  BAR%d  MEM%s%s  0x%016llx  розмір %llu\n",
               idx, is64 ? "64" : "32", pref ? " prefetch" : "",
               (unsigned long long)base,
               (unsigned long long)bar_size(b, d, f, off, is64));
    }
}
