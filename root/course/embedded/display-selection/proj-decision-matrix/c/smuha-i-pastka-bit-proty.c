/* потрібна смуга в БІТАХ за секунду для повного кадру на fps */
uint32_t required_bandwidth_bps(uint32_t w, uint32_t h,
                                ColorFormat bpp, uint32_t fps)
{
    uint32_t bits;
    /* w × h × біт_на_піксель — знову стережемося переповнення */
    if (!safe_mul3(w, h, (uint32_t)bpp, &bits))
        return UINT32_MAX;          /* сигнал «завелика площа × глибина» */
    /* × fps може перескочити 32 біти для великих екранів на 60 к/с */
    uint64_t bps = (uint64_t)bits * fps;
    return (bps > UINT32_MAX) ? UINT32_MAX : (uint32_t)bps;
}
