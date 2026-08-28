#include <stdint.h>

#define RISCV_MTVEC_MODE_DIRECT   0x00UL
#define RISCV_MTVEC_MODE_VECTORED 0x01UL

extern void riscv_trap_entry(void);
extern void __attribute__((aligned(128))) riscv_vector_table(void);

/* Встановлення прямого обробника для всіх подій */
void riscv_init_trap_direct(void) {
    uintptr_t base = (uintptr_t)&riscv_trap_entry;
    uintptr_t val = (base & ~0x3UL) | RISCV_MTVEC_MODE_DIRECT;
    __asm__ volatile ("csrw mtvec, %0" : : "r" (val) : "memory");
}

/* Встановлення векторної таблиці переривань */
void riscv_init_trap_vectored(void) {
    uintptr_t base = (uintptr_t)&riscv_vector_table;
    uintptr_t val = (base & ~0x3UL) | RISCV_MTVEC_MODE_VECTORED;
    __asm__ volatile ("csrw mtvec, %0" : : "r" (val) : "memory");
}
