enum sg_err {
    SG_OK = 0,
    SG_E_EMPTY_SEG,   // сегмент нульової довжини
    SG_E_ALIGN,       // база чи довжина не вирівняні
    SG_E_TOOMANY,     // більше сегментів, ніж бере рушій
    SG_E_OVERFLOW,    // сумарна довжина не влазить у size_t
};

// align — СТЕПІНЬ ДВІЙКИ (1 = вимог немає). O(n).
enum sg_err sg_check(const struct sg_list *sg, size_t align, int max_segs) {
    if (sg->n > max_segs) return SG_E_TOOMANY;

    const uintptr_t m = (uintptr_t)align - 1;          // маска молодших бітів
    size_t total = 0;
    for (int i = 0; i < sg->n; i++) {
        if (sg->seg[i].len == 0)                 return SG_E_EMPTY_SEG;
        if (sg->seg[i].addr & m)                 return SG_E_ALIGN;
        if ((uintptr_t)sg->seg[i].len & m)       return SG_E_ALIGN;
        if (total > SIZE_MAX - sg->seg[i].len)   return SG_E_OVERFLOW;
        total += sg->seg[i].len;
    }
    return SG_OK;
}
