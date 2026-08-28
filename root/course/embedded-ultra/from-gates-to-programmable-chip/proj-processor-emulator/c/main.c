#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#define REG_COUNT 8
#define MEM_SIZE 256

typedef enum {
    OP_NOP = 0x0,
    OP_ADD = 0x1,
    OP_SUB = 0x2,
    OP_AND = 0x3,
    OP_OR  = 0x4,
    OP_LDI = 0x5,
    OP_LD  = 0x6,
    OP_ST  = 0x7,
    OP_BEQ = 0x8,
    OP_HLT = 0xF
} Opcode;

typedef struct {
    bool z; /* Zero flag: результат операції дорівнює нулю */
    bool n; /* Negative flag: старший знаковий біт результату дорівнює 1 */
    bool c; /* Carry flag: перенос із 16-го біта / беззнакове переповнення */
    bool v; /* Overflow flag: знакове арифметичне переповнення */
} Flags;

typedef struct {
    uint16_t regs[REG_COUNT];
    uint16_t pc;
    Flags flags;
    bool halted;
    uint16_t prog_mem[MEM_SIZE];
    uint16_t data_mem[MEM_SIZE];
} CpuCore;

void cpu_init(CpuCore *cpu) {
    for (int i = 0; i < REG_COUNT; ++i) cpu->regs[i] = 0;
    cpu->pc = 0;
    cpu->flags = (Flags){ .z = false, .n = false, .c = false, .v = false };
    cpu->halted = false;
    for (int i = 0; i < MEM_SIZE; ++i) {
        cpu->prog_mem[i] = 0;
        cpu->data_mem[i] = 0;
    }
}

static int16_t sign_extend_9(uint16_t val) {
    if (val & 0x0100) {
        return (int16_t)(val | 0xFE00);
    }
    return (int16_t)(val & 0x01FF);
}

void cpu_step(CpuCore *cpu) {
    if (cpu->halted) return;

    /* 1. Фаза Fetch: вибірка слова інструкції та інкремент PC */
    uint16_t instr = cpu->prog_mem[cpu->pc % MEM_SIZE];
    cpu->pc++;

    /* 2. Фаза Decode: виділення бітових полів команди */
    uint8_t opcode = (instr >> 12) & 0x0F;
    uint8_t rd     = (instr >> 9)  & 0x07;
    uint8_t rs1    = (instr >> 6)  & 0x07;
    uint8_t rs2    = (instr >> 3)  & 0x07;
    uint16_t imm9  = instr & 0x01FF;

    /* 3. Фаза Execute / Memory / Write-Back */
    switch (opcode) {
        case OP_NOP:
            break;

        case OP_ADD: {
            uint32_t a = cpu->regs[rs1];
            uint32_t b = cpu->regs[rs2];
            uint32_t res = a + b;
            uint16_t res16 = (uint16_t)res;

            if (rd != 0) cpu->regs[rd] = res16;

            cpu->flags.z = (res16 == 0);
            cpu->flags.n = (res16 & 0x8000) != 0;
            cpu->flags.c = (res > 0xFFFF);
            cpu->flags.v = (!((a ^ b) & 0x8000) && ((a ^ res) & 0x8000));
            break;
        }

        case OP_SUB: {
            uint32_t a = cpu->regs[rs1];
            uint32_t b = cpu->regs[rs2];
            uint32_t res = a - b;
            uint16_t res16 = (uint16_t)res;

            if (rd != 0) cpu->regs[rd] = res16;

            cpu->flags.z = (res16 == 0);
            cpu->flags.n = (res16 & 0x8000) != 0;
            cpu->flags.c = (a >= b);
            cpu->flags.v = (((a ^ b) & 0x8000) && ((a ^ res) & 0x8000));
            break;
        }

        case OP_AND: {
            uint16_t res = cpu->regs[rs1] & cpu->regs[rs2];
            if (rd != 0) cpu->regs[rd] = res;
            cpu->flags.z = (res == 0);
            cpu->flags.n = (res & 0x8000) != 0;
            break;
        }

        case OP_OR: {
            uint16_t res = cpu->regs[rs1] | cpu->regs[rs2];
            if (rd != 0) cpu->regs[rd] = res;
            cpu->flags.z = (res == 0);
            cpu->flags.n = (res & 0x8000) != 0;
            break;
        }

        case OP_LDI: {
            int16_t ext = sign_extend_9(imm9);
            if (rd != 0) cpu->regs[rd] = (uint16_t)ext;
            break;
        }

        case OP_LD: {
            uint16_t addr = cpu->regs[rs1] % MEM_SIZE;
            if (rd != 0) cpu->regs[rd] = cpu->data_mem[addr];
            break;
        }

        case OP_ST: {
            uint16_t addr = cpu->regs[rs1] % MEM_SIZE;
            cpu->data_mem[addr] = cpu->regs[rs2];
            break;
        }

        case OP_BEQ: {
            if (cpu->regs[rd] == cpu->regs[rs1]) {
                int16_t offset = sign_extend_9(imm9);
                cpu->pc = (uint16_t)((int16_t)cpu->pc + offset);
            }
            break;
        }

        case OP_HLT:
            cpu->halted = true;
            break;

        default:
            cpu->halted = true;
            break;
    }

    cpu->regs[0] = 0; /* R0 апаратно підключений до землі (незмінний 0) */
}
