typedef enum {
    VERDICT_FITS,            /* влазить у намічений МК як є        */
    VERDICT_NEED_BETTER_MCU, /* потрібен дорожчий МК (RAM чи смуга) */
    VERDICT_REDUCE_RES,      /* фізично завелике — зменшити роздільність */
    VERDICT_OVERFLOW,        /* числа переповнюють навіть 32 біти  */
} Verdict;

typedef struct {
    uint32_t w, h;
    ColorFormat bpp;
    uint32_t fps;              /* бажана частота оновлення повного кадру */
    bool panel_has_gram;      /* true = памʼять кадру в панелі (SPI+GRAM) */
} DisplaySpec;

typedef struct {
    uint32_t free_ram_bytes;   /* вільна RAM хоста під кадровий буфер */
    uint32_t bus_clock_bps;    /* тактова шини до панелі, біт/с        */
} McuSpec;

Verdict budget_verdict(const DisplaySpec *d, const McuSpec *m)
{
    /* --- перевірка 1: памʼять (лише якщо буфер тримає хост) --- */
    uint32_t fb = 0;
    if (!d->panel_has_gram) {
        if (!safe_mul3(d->w, d->h, bytes_per_pixel(d->bpp), &fb))
            return VERDICT_OVERFLOW;           /* завелика площа × глибина */
        if (fb > m->free_ram_bytes) {
            /* буфер не влазить у RAM хоста. Чи це «дорожчий МК»,
               чи «зменшити роздільність» — вирішує, наскільки не
               влазить: якщо навіть удвічі менший не влізе, то це
               вже клас із зовнішньою RAM. Поріг тут — інженерний. */
            return (fb > 2u * m->free_ram_bytes)
                   ? VERDICT_REDUCE_RES
                   : VERDICT_NEED_BETTER_MCU;
        }
    }

    /* --- перевірка 2: смуга (для будь-якого інтерфейсу) --- */
    uint32_t need_bps = required_bandwidth_bps(d->w, d->h, d->bpp, d->fps);
    if (need_bps == UINT32_MAX)
        return VERDICT_OVERFLOW;
    if (need_bps > m->bus_clock_bps)
        return VERDICT_NEED_BETTER_MCU;        /* смуги не вистачає */

    return VERDICT_FITS;
}
