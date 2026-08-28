#include <stdbool.h>

/* Прямий стрибок на мітку error_handler у разі виникнення переносу */
bool check_add_overflow(unsigned long a, unsigned long b, unsigned long *res) {
    __asm__ __volatile__ goto (
        "addq %[val], %[dest]\n\t"
        "jc %l[overflow_label]"
        : [dest] "+r" (a)
        : [val] "r" (b)
        : "cc"
        : overflow_label
    );
    
    *res = a;
    return false;

overflow_label:
    return true;
}
