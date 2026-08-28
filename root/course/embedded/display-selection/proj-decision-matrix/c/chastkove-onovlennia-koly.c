/* час пересилання прямокутної латки w×h по шині, у мікросекундах */
uint32_t partial_update_us(uint32_t w, uint32_t h, ColorFormat bpp,
                           uint32_t bus_clock_bps)
{
    uint32_t bits;
    if (!safe_mul3(w, h, (uint32_t)bpp, &bits))
        return UINT32_MAX;
    /* час(с) = біт / (біт/с); у мікросекундах — × 1 000 000.
       рахуємо в 64 бітах, щоб bits × 1e6 не переповнилось */
    uint64_t us = (uint64_t)bits * 1000000u / bus_clock_bps;
    return (us > UINT32_MAX) ? UINT32_MAX : (uint32_t)us;
}
