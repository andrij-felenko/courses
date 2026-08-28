#define REPS  200u

void profile_rms(const uint16_t *raw, size_t n) {
    cyccnt_enable();
    volatile float sink = 0;                 // volatile — щоб компілятор не викинув виклик
    uint32_t t0 = cyccnt();
    for (unsigned r = 0; r < REPS; r++)
        sink += compute_rms_mA(raw, n);
    uint32_t dt = cyccnt() - t0;
    printf("naive: %lu cycles/call, %lu cycles/sample\n",
           (unsigned long)(dt / REPS),
           (unsigned long)(dt / REPS / n));
}
