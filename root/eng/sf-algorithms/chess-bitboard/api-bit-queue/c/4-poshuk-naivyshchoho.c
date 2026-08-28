int bitq64_find_highest(const BitQueue64 *q) {
    if (q->mask == 0) {
        return -1;
    }
    #if defined(_MSC_VER)
    unsigned long idx;
    _BitScanForward64(&idx, q->mask);
    return (int)idx;
    #else
    return __builtin_ctzll(q->mask);
    #endif
}
