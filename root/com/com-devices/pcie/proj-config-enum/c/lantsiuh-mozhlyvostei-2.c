static void dump_link(uint8_t b, uint8_t d, uint8_t f)
{
    static const char *gts[] = { "?", "2.5", "5.0", "8.0", "16.0", "32.0", "64.0" };

    uint8_t cap = find_cap(b, d, f, 0x10);
    if (!cap) return;                                /* не PCIe, а старий PCI-пристрій */

    uint16_t sta = cfg_r16(b, d, f, (uint16_t)(cap + 0x12));   /* Link Status */
    unsigned speed =  sta       & 0x0Fu;             /* 1→2.5 … 6→64 ГТ/с */
    unsigned width = (sta >> 4) & 0x3Fu;             /* стільки смуг натренувалося */

    printf("  з'єднання: %s ГТ/с ×%u\n",
           speed < 7 ? gts[speed] : "?", width);
}
