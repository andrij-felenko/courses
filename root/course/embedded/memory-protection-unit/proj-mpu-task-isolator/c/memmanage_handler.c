#include "mpu_isolator.h"

/*
 * Асемблерна обгортка переривання MemManage_Handler.
 * Головне завдання: перевірити біт 2 регістру LR (EXC_RETURN),
 * щоб визначити, на якому покажчику стека (MSP чи PSP) знаходиться
 * апаратний стек-фрейм винятку, та передати цей вказівник у функцію C.
 */
#if defined(__GNUC__) || defined(__clang__)
__attribute__((naked)) void MemManage_Handler(void) {
    __asm volatile(
        "tst lr, #4        \n" /* Перевірка біта 2 EXC_RETURN */
        "ite eq            \n"
        "mrseq r0, msp     \n" /* Якщо біт 2 = 0, стек був Main Stack Pointer (MSP) */
        "mrsne r0, psp     \n" /* Якщо біт 2 = 1, стек був Process Stack Pointer (PSP) */
        "mov r1, lr        \n" /* Другий аргумент r1 = значення EXC_RETURN */
        "b mpu_memmanage_c_handler \n" /* Перехід до C-обробника */
    );
}
#else
void MemManage_Handler(void) {
    /* Для середовищ емуляції без GCC/Clang asm */
    mpu_memmanage_c_handler(NULL, 0xFFFFFFFDUL);
}
#endif
