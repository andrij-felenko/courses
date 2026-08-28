/* Примусова серіалізація конвеєра для зупинки спекулятивного виконання (LFENCE / CSDB) */
static inline void ct_speculation_barrier(void) {
    #if defined(__x86_64__) || defined(_M_X64)
    #if defined(__GNUC__) || defined(__clang__)
    __asm__ volatile ("lfence" ::: "memory");
    #else
    _mm_lfence();
    #endif
    #elif defined(__aarch64__)
    __asm__ volatile ("isb" ::: "memory");
    #else
    CT_BARRIER_32(0);
    #endif
}

/* Безпечне обмеження індексу масиву без умовних переходів для запобігання Spectre-v1 */
static inline size_t ct_speculative_clamp_index(size_t idx, size_t max_len) {
    /* Якщо idx < max_len, маска = 0xFF..FF, інакше 0x00..00 */
    size_t diff = idx ^ max_len;
    size_t sub = idx - max_len;
    size_t borrow = (idx & ~max_len) | ((~diff) & sub);
    size_t mask = -((borrow >> ((sizeof(size_t) * 8) - 1)) & 1);
    
    #if defined(__GNUC__) || defined(__clang__)
    __asm__ volatile ("" : "+r" (mask));
    #endif
    
    return idx & mask;
}
