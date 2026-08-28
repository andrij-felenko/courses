#include <stdint.h>
#include <stdio.h>

/* Зчитування TSC на x86-64 із серіалізацією конвеєра через lfence */
static inline uint64_t cpu_cycles_x86(void) {
    uint32_t lo, hi;
    /* lfence запобігає випереджальному виконанню rdtsc процесором */
    __asm__ __volatile__ (
        "lfence\n\t"
        "rdtsc"
        : "=a" (lo), "=d" (hi)
        :
        : "memory"
    );
    return ((uint64_t)hi << 32) | lo;
}

/* Зчитування віртуального лічильника CNTVCT_EL0 на ARM64 */
static inline uint64_t cpu_cycles_arm64(void) {
    uint64_t val;
    __asm__ __volatile__ (
        "isb\n\t"
        "mrs %0, cntvct_el0"
        : "=r" (val)
        :
        : "memory"
    );
    return val;
}

int main(void) {
    uint64_t start = cpu_cycles_x86();
    
    /* Вимірювана ділянка коду: простий накопичувальний цикл */
    volatile int sum = 0;
    for (int i = 0; i < 1000; ++i) {
        sum += i;
    }
    
    uint64_t end = cpu_cycles_x86();
    printf("Витрачено тактів процесора: %lu\n", (unsigned long)(end - start));
    return 0;
}
