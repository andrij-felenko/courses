volatile struct {
    uint8_t count_lo;
    uint8_t count_hi;
    uint8_t overflow_flag;
} ctr;

void tick(void) {
    ctr.count_lo++;
    if (ctr.count_lo == 0) {
        ctr.count_hi++;
        if (ctr.count_hi == 0)
            ctr.overflow_flag = 1;
    }
}
