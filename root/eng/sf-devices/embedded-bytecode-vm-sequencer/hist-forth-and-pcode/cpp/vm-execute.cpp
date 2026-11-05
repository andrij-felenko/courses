#include <stdint.h>
#include <stdbool.h>

#define STACK_SIZE 16

typedef enum {
    OP_NOP = 0,
    OP_PUSH_BYTE,
    OP_ADD,
    OP_SUB,
    OP_JMP_IF_ZERO,
    OP_HALT
} opcode_t;

typedef struct {
    const uint8_t *pc;                  // Покажчик команд (Program Counter)
    int16_t data_stack[STACK_SIZE];     // Стек даних
    uint8_t dsp;                        // Покажчик стека даних (Data Stack Pointer)
    bool running;
} vm_t;

void vm_execute(vm_t *vm, const uint8_t *code) {
    vm->pc = code;
    vm->dsp = 0;
    vm->running = true;

    // Таблиця переходів GCC computed GOTO для виключення оверхеду switch-case
    static const void *dispatch_table[] = {
        [OP_NOP]         = &&handle_nop,
        [OP_PUSH_BYTE]   = &&handle_push,
        [OP_ADD]         = &&handle_add,
        [OP_SUB]         = &&handle_sub,
        [OP_JMP_IF_ZERO] = &&handle_jmp_zero,
        [OP_HALT]        = &&handle_halt
    };

    #define DISPATCH() goto *dispatch_table[*vm->pc++]

    // Стартова диспетчеризація першої інструкції
    DISPATCH();

handle_nop:
    DISPATCH();

handle_push:
    if (vm->dsp < STACK_SIZE) {
        vm->data_stack[vm->dsp++] = (int8_t)*vm->pc++;
    }
    DISPATCH();

handle_add:
    if (vm->dsp >= 2) {
        int16_t b = vm->data_stack[--vm->dsp];
        int16_t a = vm->data_stack[--vm->dsp];
        vm->data_stack[vm->dsp++] = a + b;
    }
    DISPATCH();

handle_sub:
    if (vm->dsp >= 2) {
        int16_t b = vm->data_stack[--vm->dsp];
        int16_t a = vm->data_stack[--vm->dsp];
        vm->data_stack[vm->dsp++] = a - b;
    }
    DISPATCH();

handle_jmp_zero: {
    uint8_t target_offset = *vm->pc++;
    int16_t val = vm->data_stack[--vm->dsp];
    if (val == 0) {
        vm->pc = code + target_offset;
    }
    DISPATCH();
}

handle_halt:
    vm->running = false;
    #undef DISPATCH
}
