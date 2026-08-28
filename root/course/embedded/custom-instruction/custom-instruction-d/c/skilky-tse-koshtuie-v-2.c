/* popcount_ci() компілюється в ОДНУ машинну команду.
   Схема в тракті ядра рахує всі 32 біти паралельно за такт. */
static inline uint32_t popcount_ci(uint32_t x) {
    uint32_t r;
    /* асемблерна вставка: наш зарезервований опкод, rs1=x -> rd=r */
    asm volatile ("popcount %0, %1" : "=r"(r) : "r"(x));
    return r;
}

uint32_t hamming_distance(uint32_t a, uint32_t b) {
    return popcount_ci(a ^ b);   /* біти, що різняться, — за два такти разом */
}
