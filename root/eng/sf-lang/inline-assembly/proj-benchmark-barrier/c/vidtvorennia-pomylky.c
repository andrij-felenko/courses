#include <stdint.h>
#include <stdio.h>

/* ДЕФЕКТ: при оптимізації -O2 змінна multiplier буде пошкоджена */
uint64_t unsafe_accumulate(uint64_t base, uint64_t multiplier) {
    uint64_t result;
    __asm__ (
        "movq %1, %0\n\t"       /* Крок 1: запис у %0 руйнує %2, якщо вони в одному регістрі! */
        "imulq %2, %0\n\t"      /* Крок 2: множення на вже пошкоджений %2 */
        "addq %1, %0"           /* Крок 3: додавання base */
        : "=r" (result)         /* ПОМИЛКА: пропущено модифікатор & */
        : "r" (base), "r" (multiplier)
        : "cc"
    );
    return result;
}
