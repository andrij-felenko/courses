#include <stdint.h>

#define VTOR (*(volatile uint32_t *)0xE000ED08u)  // Vector Table Offset Register

static inline void dsb(void) { __asm volatile ("dsb 0xF" ::: "memory"); }
static inline void isb(void) { __asm volatile ("isb 0xF" ::: "memory"); }

void relocate_vectors(uint32_t *new_table)
{
    // new_table мусить бути вирівняний за правилами ядра (типово на розмір
    // таблиці, округлений угору до степеня двійки; часто 512 байт).
    VTOR = (uint32_t)new_table;  // переставити базу таблиці
    dsb();  // дочекатися, поки запис у VTOR справді набуде чинності…
    isb();  // …і щоб наступне переривання пішло вже за НОВОЮ таблицею
}
