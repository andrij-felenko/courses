#include "vector_table_types.h"

#define SCB_ICIALLU_REG      (*(volatile uint32_t*)(0xE000EF50UL))
#define SCB_DCCMVAC_REG      (*(volatile uint32_t*)(0xE000EF68UL))
#define SCB_DCIMVAC_REG      (*(volatile uint32_t*)(0xE000EF5CUL))
#define SCB_DCCIMVAC_REG     (*(volatile uint32_t*)(0xE000EF70UL))

#define L1_CACHE_LINE_BYTES  32U

static inline void dsb(void) { __asm__ volatile ("dsb 0xF" : : : "memory"); }
static inline void isb(void) { __asm__ volatile ("isb 0xF" : : : "memory"); }

void cache_flush_and_invalidate_range(uintptr_t start_addr, size_t length) {
    uintptr_t current = start_addr & ~(L1_CACHE_LINE_BYTES - 1UL);
    const uintptr_t end = start_addr + length;

    /* Порядкове скидання брудних ліній D-Cache у фізичну оперативну пам'ять */
    while (current < end) {
        SCB_DCCMVAC_REG = current;
        current += L1_CACHE_LINE_BYTES;
    }
    dsb();

    /* Знедійнення всього кешу інструкцій */
    SCB_ICIALLU_REG = 0;
    dsb();
    isb();
}
