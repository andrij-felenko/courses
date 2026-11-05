#include <stdint.h>
#include <stdbool.h>

#define VM_STACK_DEPTH 8
#define VM_NUM_REGS    4

typedef enum {
    VM_STATUS_IDLE = 0,
    VM_STATUS_RUNNING,
    VM_STATUS_WAITING,
    VM_ERROR_INVALID_OPCODE,
    VM_ERROR_STACK_OVERFLOW,
    VM_ERROR_STACK_UNDERFLOW,
    VM_ERROR_OUT_OF_BOUNDS
} vm_status_t;

typedef enum {
    OP_NOP      = 0x00,
    OP_JMP      = 0x01,
    OP_CALL     = 0x03,
    OP_RET      = 0x04,
    OP_YIELD    = 0x05,
    OP_WAIT     = 0x06,
    OP_GPIO_SET = 0x10
} vm_opcode_t;

typedef struct {
    const uint8_t *code;
    uint16_t code_size;
    uint16_t ip;
    uint16_t stack[VM_STACK_DEPTH];
    uint8_t sp;
    int32_t registers[VM_NUM_REGS];
    uint32_t wait_until_ms;
    vm_status_t status;
} vm_context_t;

void vm_init(vm_context_t *ctx, const uint8_t *code, uint16_t size) {
    ctx->code = code;
    ctx->code_size = size;
    ctx->ip = 0;
    ctx->sp = 0;
    ctx->wait_until_ms = 0;
    ctx->status = VM_STATUS_RUNNING;
    for (int i = 0; i < VM_NUM_REGS; i++) {
        ctx->registers[i] = 0;
    }
}

// Фіктивний виклик платформного системного часу в мілісекундах
extern uint32_t sys_now_ms(void);
// Фіктивний виклик керування GPIO виводом
extern void hal_gpio_write(uint8_t pin, uint8_t val);

vm_status_t vm_step(vm_context_t *ctx) {
    if (ctx->status == VM_STATUS_WAITING) {
        if (sys_now_ms() >= ctx->wait_until_ms) {
            ctx->status = VM_STATUS_RUNNING;
        } else {
            return ctx->status;
        }
    }

    if (ctx->status != VM_STATUS_RUNNING) {
        return ctx->status;
    }

    if (ctx->ip >= ctx->code_size) {
        ctx->status = VM_ERROR_OUT_OF_BOUNDS;
        return ctx->status;
    }

    uint8_t opcode = ctx->code[ctx->ip++];

    switch (opcode) {
        case OP_NOP:
            break;

        case OP_JMP: {
            if (ctx->ip + 2 > ctx->code_size) {
                ctx->status = VM_ERROR_OUT_OF_BOUNDS;
                break;
            }
            uint16_t target = (uint16_t)ctx->code[ctx->ip] | 
                             ((uint16_t)ctx->code[ctx->ip + 1] << 8);
            ctx->ip = target;
            break;
        }

        case OP_CALL: {
            if (ctx->ip + 2 > ctx->code_size) {
                ctx->status = VM_ERROR_OUT_OF_BOUNDS;
                break;
            }
            if (ctx->sp >= VM_STACK_DEPTH) {
                ctx->status = VM_ERROR_STACK_OVERFLOW;
                break;
            }
            uint16_t target = (uint16_t)ctx->code[ctx->ip] | 
                             ((uint16_t)ctx->code[ctx->ip + 1] << 8);
            ctx->stack[ctx->sp++] = ctx->ip + 2;
            ctx->ip = target;
            break;
        }

        case OP_RET: {
            if (ctx->sp == 0) {
                ctx->status = VM_ERROR_STACK_UNDERFLOW;
                break;
            }
            ctx->ip = ctx->stack[--ctx->sp];
            break;
        }

        case OP_YIELD:
            // Тимчасово передаємо управління головному циклу
            return VM_STATUS_WAITING;

        case OP_WAIT: {
            if (ctx->ip + 2 > ctx->code_size) {
                ctx->status = VM_ERROR_OUT_OF_BOUNDS;
                break;
            }
            uint16_t delay_ms = (uint16_t)ctx->code[ctx->ip] | 
                               ((uint16_t)ctx->code[ctx->ip + 1] << 8);
            ctx->ip += 2;
            ctx->wait_until_ms = sys_now_ms() + delay_ms;
            ctx->status = VM_STATUS_WAITING;
            break;
        }

        case OP_GPIO_SET: {
            if (ctx->ip + 2 > ctx->code_size) {
                ctx->status = VM_ERROR_OUT_OF_BOUNDS;
                break;
            }
            uint8_t pin = ctx->code[ctx->ip++];
            uint8_t val = ctx->code[ctx->ip++];
            hal_gpio_write(pin, val);
            break;
        }

        default:
            ctx->status = VM_ERROR_INVALID_OPCODE;
            break;
    }

    return ctx->status;
}
