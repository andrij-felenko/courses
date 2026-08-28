#include <stdbool.h>
#include <stdio.h>

void execute_fast_math(int a, int b) {
    /* asm goto виконує прямий стрибок на мітку overflow_detected */
    __asm__ __volatile__ goto (
        "addl %1, %0\n\t"
        "jo %l[overflow_detected]" /* Jump if Overflow прямо на C-мітку */
        :
        : "r" (a), "r" (b)
        : "cc"
        : overflow_detected
    );
    
    printf("Обчислення успішне, переповнення немає.\n");
    return;

overflow_detected:
    fprintf(stderr, "Помилка: арифметичне переповнення!\n");
}
