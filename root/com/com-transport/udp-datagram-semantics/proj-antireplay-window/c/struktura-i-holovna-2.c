static int arw_popcount64(uint64_t x)
{
#if defined(__GNUC__) || defined(__clang__)
    return __builtin_popcountll(x);
#else
    x = x - ((x >> 1) & 0x5555555555555555ULL);
    x = (x & 0x3333333333333333ULL) + ((x >> 2) & 0x3333333333333333ULL);
    x = (x + (x >> 4)) & 0x0F0F0F0F0F0F0F0FULL;
    return (int)((x * 0x0101010101010101ULL) >> 56);
#endif
}

/* Скільки позицій вікна відповідають номерам, які справді існували.
   Одразу після старту вікно «висить» над номерами, яких відправник ще
   не слав, — без цієї поправки вони порахуються втраченими. */
static unsigned arw_live(const arw *w)
{
    uint64_t span = (uint64_t)(uint32_t)(w->top - w->first) + 1;
    return span < ARW_BITS ? (unsigned)span : ARW_BITS;
}
