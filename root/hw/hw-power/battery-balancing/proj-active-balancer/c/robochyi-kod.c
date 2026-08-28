static void find_extremes(const uint16_t v[NCELLS], uint8_t *hi, uint8_t *lo)
{
    uint8_t imax = 0u, imin = 0u;
    for (uint8_t i = 1u; i < NCELLS; ++i) {
        if (v[i] > v[imax]) imax = i;
        if (v[i] < v[imin]) imin = i;
    }
    *hi = imax;
    *lo = imin;
}

static bool window_open(void)
{
    int32_t i = pack_current_ma();
    if (i < 0) i = -i;
    if (i > IPACK_MAX_MA) return false;   // під струмом напруга бреше (IR-падіння)
    return charger_in_cv();               // балансуємо у крутій верхівці OCV
}
