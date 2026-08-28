#define VENDOR_NONE 0xFFFFu

static void     scan_bus(uint8_t bus);      /* взаємна рекурсія зі scan_function */
static void     decode_bars(uint8_t b, uint8_t d, uint8_t f, int count);
static uint64_t bar_size(uint8_t b, uint8_t d, uint8_t f, uint16_t off, int is64);
static void     dump_link(uint8_t b, uint8_t d, uint8_t f);

static void scan_function(uint8_t bus, uint8_t dev, uint8_t fn)
{
    uint16_t vid = cfg_r16(bus, dev, fn, 0x00);
    uint16_t did = cfg_r16(bus, dev, fn, 0x02);
    uint32_t cls = cfg_r32(bus, dev, fn, 0x08) >> 8;    /* клас, підклас, інтерфейс */
    uint8_t  hdr = cfg_r8 (bus, dev, fn, 0x0E) & 0x7Fu; /* тип заголовка без біта багатофункційності */

    printf("%02x:%02x.%u  %04x:%04x  клас %06x\n",
           (unsigned)bus, (unsigned)dev, (unsigned)fn,
           (unsigned)vid, (unsigned)did, (unsigned)cls);

    if (hdr == 0x00) {                       /* кінцевий пристрій: шість BAR-ів */
        decode_bars(bus, dev, fn, 6);
    } else if (hdr == 0x01) {                /* міст: два власні BAR-и й ціла шина за ним */
        decode_bars(bus, dev, fn, 2);
        uint8_t sec = cfg_r8(bus, dev, fn, 0x19);
        if (sec > bus)                       /* захист від циклу на кривому залізі */
            scan_bus(sec);
    }
    dump_link(bus, dev, fn);
}

static void scan_device(uint8_t bus, uint8_t dev)
{
    if (cfg_r16(bus, dev, 0, 0x00) == VENDOR_NONE)
        return;                              /* нема функції 0 — нема пристрою взагалі */

    scan_function(bus, dev, 0);

    if ((cfg_r8(bus, dev, 0, 0x0E) & 0x80u) == 0)
        return;                              /* однофункційний — решту сімки не питаємо */

    for (uint8_t fn = 1; fn < 8; fn++)
        if (cfg_r16(bus, dev, fn, 0x00) != VENDOR_NONE)
            scan_function(bus, dev, fn);
}

static void scan_bus(uint8_t bus)
{
    for (uint8_t dev = 0; dev < 32; dev++)
        scan_device(bus, dev);
}

int main(void)
{
    ecam = map_ecam(mcfg_base_of_segment(0), 256u << 20);
    scan_bus(0);
    return 0;
}
