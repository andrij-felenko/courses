#include <stdint.h>
#include <stdbool.h>

#define VM_STACK_DEPTH 4
#define VM_NUM_REGS    4

typedef enum {
    VM_STATUS_IDLE = 0,
    VM_STATUS_RUNNING,
    VM_STATUS_WAITING,
    VM_STATUS_HALTED,
    VM_STATUS_ERROR_STACK_OVERFLOW,
    VM_STATUS_ERROR_STACK_UNDERFLOW,
    VM_STATUS_ERROR_INVALID_OPCODE
} vm_status_t;

typedef struct {
    uint16_t ip;                        // Покажчик інструкцій (зміщення в байткоді)
    uint16_t registers[VM_NUM_REGS];    // Робочі регістри R0..R3
    uint32_t delay_until_ms;            // Часова мітка закінчення неблокуючої затримки
    uint16_t stack[VM_STACK_DEPTH];     // Фіксований стек адрес повернення (CALL/RET)
    uint8_t sp;                         // Покажчик стеку (індекс вершини)
    vm_status_t status;                 // Поточний стан віртуальної машини
    const uint8_t *code;                // Указник на масив байткоду у Flash
    uint16_t code_len;                  // Довжина масиву байткоду
} vm_context_t;

void vm_init(vm_context_t *ctx, const uint8_t *code, uint16_t code_len) {
    ctx->ip = 0;
    for (int i = 0; i < VM_NUM_REGS; i++) {
        ctx->registers[i] = 0;
    }
    ctx->delay_until_ms = 0;
    for (int i = 0; i < VM_STACK_DEPTH; i++) {
        ctx->stack[i] = 0;
    }
    ctx->sp = 0;
    ctx->status = VM_STATUS_IDLE;
    ctx->code = code;
    ctx->code_len = code_len;
}
