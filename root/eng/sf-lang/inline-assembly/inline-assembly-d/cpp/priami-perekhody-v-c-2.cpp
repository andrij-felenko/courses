#include <iostream>

void execute_fast_math(int a, int b) noexcept {
    asm volatile goto (
        "addl %1, %0\n\t"
        "jo %l[overflow_detected]"
        :
        : "r" (a), "r" (b)
        : "cc"
        : overflow_detected
    );
    
    std::cout << "Обчислення успішне, переповнення немає.\n";
    return;

overflow_detected:
    std::cerr << "Помилка: арифметичне переповнення!\n";
}
