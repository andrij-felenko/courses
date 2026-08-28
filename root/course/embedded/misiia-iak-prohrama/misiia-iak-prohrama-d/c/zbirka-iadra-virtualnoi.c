#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_ITEMS        64
#define MAX_TOTAL_JUMPS  128

typedef enum {
    OP_HALT          = 0,
    OP_WAYPOINT      = 1,
    OP_JUMP          = 2,
    OP_CHECK_BATTERY = 3
} opcode_t;

typedef struct {
    opcode_t opcode;
    uint16_t target;
    uint16_t param;
    float    lat;
    float    lon;
    float    alt;
} instr_t;

typedef struct {
    instr_t  code[MAX_ITEMS];
    uint16_t code_len;
    uint16_t pc;
    uint16_t jump_counts[MAX_ITEMS];
    uint16_t total_jumps;
    bool     finished;
    bool     error_infinite_loop;
} vm_core_t;

void vm_init(vm_core_t *vm, const instr_t *program, uint16_t len) {
    memset(vm, 0, sizeof(vm_core_t));
    if (len > MAX_ITEMS) len = MAX_ITEMS;
    memcpy(vm->code, program, len * sizeof(instr_t));
    vm->code_len = len;
    vm->pc = 0;
}

void vm_tick(vm_core_t *vm, float bat_soc_pct, bool wp_reached) {
    if (vm->finished || vm->error_infinite_loop || vm->pc >= vm->code_len) {
        vm->finished = true;
        return;
    }

    const instr_t *curr = &vm->code[vm->pc];

    switch (curr->opcode) {
        case OP_HALT:
            vm->finished = true;
            break;

        case OP_WAYPOINT:
            if (wp_reached) {
                vm->pc++;
            }
            break;

        case OP_CHECK_BATTERY:
            if (bat_soc_pct < (float)curr->param) {
                vm->pc = curr->target; /* Стрибок на аварійну гілку */
            } else {
                vm->pc++;
            }
            break;

        case OP_JUMP:
            if (vm->total_jumps >= MAX_TOTAL_JUMPS) {
                vm->error_infinite_loop = true;
                break;
            }

            if (vm->jump_counts[vm->pc] < curr->param) {
                vm->jump_counts[vm->pc]++;
                vm->total_jumps++;
                vm->pc = curr->target;
            } else {
                vm->jump_counts[vm->pc] = 0; /* Скидання для наступних входів */
                vm->pc++;
            }
            break;
    }
}
