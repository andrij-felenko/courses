#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef enum {
    VM_ERR_NONE             = 0x00,
    VM_ERR_STACK_OVERFLOW   = 0x01,
    VM_ERR_STACK_UNDERFLOW  = 0x02,
    VM_ERR_INVALID_OPCODE   = 0x03,
    VM_ERR_OUT_OF_BOUNDS    = 0x04
} vm_error_code_t;

typedef struct {
    uint8_t error_code;
    uint16_t fault_ip;
    uint8_t fault_sp;
    uint16_t stack_snapshot[8];
    uint16_t regs_snapshot[4];
} vm_crash_dump_t;

void vm_save_crash_dump(const vm_crash_dump_t *dump) {
    printf("[VM CRASH DUMP] Error: 0x%02X at IP: 0x%04X, SP: %d\n",
           dump->error_code, dump->fault_ip, dump->fault_sp);
    for (int i = 0; i < dump->fault_sp; ++i) {
        printf("  Stack[%d] = 0x%04X\n", i, dump->stack_snapshot[i]);
    }
}

void vm_trigger_fault(vm_error_code_t code, uint16_t ip, uint8_t sp, 
                      const uint16_t *stack, const uint16_t *regs) {
    vm_crash_dump_t dump;
    dump.error_code = code;
    dump.fault_ip = ip;
    dump.fault_sp = sp;
    memcpy(dump.stack_snapshot, stack, sizeof(uint16_t) * (sp < 8 ? sp : 8));
    memcpy(dump.regs_snapshot, regs, sizeof(uint16_t) * 4);
    
    vm_save_crash_dump(&dump);
}
