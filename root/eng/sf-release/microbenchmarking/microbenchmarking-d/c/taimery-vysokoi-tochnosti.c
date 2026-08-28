/* Читання серіалізованого лічильника тактів на C */
static inline uint64_t rdtsc_start(void) {
    uint32_t cycles_high, cycles_low;
    asm volatile("lfence\n\t"
                 "rdtsc\n\t"
                 : "=a"(cycles_low), "=d"(cycles_high));
    return ((uint64_t)cycles_high << 32) | cycles_low;
}

static inline uint64_t rdtsc_end(void) {
    uint32_t cycles_high, cycles_low;
    asm volatile("rdtscp\n\t"
                 "lfence\n\t"
                 : "=a"(cycles_low), "=d"(cycles_high)
                 :
                 : "rcx");
    return ((uint64_t)cycles_high << 32) | cycles_low;
}
