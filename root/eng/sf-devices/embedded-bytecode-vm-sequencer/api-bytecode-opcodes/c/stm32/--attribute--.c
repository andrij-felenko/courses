#include <stdint.h>
#include <stdbool.h>

#define VM_STACK_DEPTH 8
#define VM_REG_COUNT   4

typedef enum {
    OP_NOP      = 0x00,
    OP_SET_GPIO = 0x01,
    OP_READ_ADC = 0x02,
    OP_JMP      = 0x03,
    OP_CALL     = 0x04,
    OP_RET      = 0x05,
    OP_WAIT_MS  = 0x06,
    OP_YIELD    = 0x07,
    OP_HALT     = 0xFF
} vm_opcode_t;

typedef struct __attribute__((packed)) {
    uint16_t ip;
    uint16_t stack[VM_STACK_DEPTH];
    uint16_t regs[VM_REG_COUNT];
    uint32_t wait_until_ms;
    uint8_t sp;
    bool is_running;
    bool is_waiting;
} vm_state_t;

static inline uint8_t vm_fetch_byte(const uint8_t *code, uint16_t *ip) {
    return code[(*ip)++];
}

static inline uint16_t vm_fetch_word(const uint8_t *code, uint16_t *ip) {
    uint16_t val = (uint16_t)code[*ip] | ((uint16_t)code[*ip + 1] << 8);
    *ip += 2;
    return val;
}

bool vm_step(vm_state_t *vm, const uint8_t *code, uint16_t code_len, uint32_t current_ms) {
    if (!vm->is_running) return false;
    
    if (vm->is_waiting) {
        if (current_ms >= vm->wait_until_ms) {
            vm->is_waiting = false;
        } else {
            return true;
        }
    }

    if (vm->ip >= code_len) {
        vm->is_running = false;
        return false;
    }

    uint8_t opcode = vm_fetch_byte(code, &vm->ip);

    switch (opcode) {
        case OP_NOP:
            break;

        case OP_SET_GPIO: {
            uint8_t pin = vm_fetch_byte(code, &vm->ip);
            uint8_t val = vm_fetch_byte(code, &vm->ip);
            (void)pin; (void)val;
            break;
        }

        case OP_WAIT_MS: {
            uint16_t delay = vm_fetch_word(code, &vm->ip);
            vm->wait_until_ms = current_ms + delay;
            vm->is_waiting = true;
            break;
        }

        case OP_JMP: {
            uint16_t target = vm_fetch_word(code, &vm->ip);
            if (target >= code_len) {
                vm->is_running = false;
                return false;
            }
            vm->ip = target;
            break;
        }

        case OP_CALL: {
            uint16_t target = vm_fetch_word(code, &vm->ip);
            if (vm->sp >= VM_STACK_DEPTH || target >= code_len) {
                vm->is_running = false;
                return false;
            }
            vm->stack[vm->sp++] = vm->ip;
            vm->ip = target;
            break;
        }

        case OP_RET: {
            if (vm->sp == 0) {
                vm->is_running = false;
                return false;
            }
            vm->ip = vm->stack[--vm->sp];
            break;
        }

        case OP_YIELD:
            return true;

        case OP_HALT:
            vm->is_running = false;
            return false;

        default:
            vm->is_running = false;
            return false;
    }

    return true;
}
