#include <stdint.h>
#include <stdbool.h>

#define GUEST_REGS_COUNT 32

typedef struct CPUState {
    uint32_t regs[GUEST_REGS_COUNT]; // Регістри загального призначення (R0-R31)
    uint32_t pc;                     // Гостьовий лічильник команд (Program Counter)
    uint32_t sp;                     // Вказівник стека
    
    // Поля лінивого обчислення прапорців стану
    uint32_t cc_op;                  // Код останньої операції (ADD, SUB, AND...)
    uint32_t cc_src1;                // Перший вхідний операнд
    uint32_t cc_src2;                // Другий вхідний операнд
    uint32_t cc_dst;                 // Результат операції
    
    // Бюджет інструкцій для детермінованих таймерів та переривань
    int32_t  icount_budget;
    
    bool     halted;                 // Прапорець зупинки процесора
    uint32_t pending_interrupts;     // Бітова маска активних ліній переривань
} CPUState;
