#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

typedef enum { OP_INC, OP_DEC_JNZ, OP_HALT } OpCode;

typedef struct {
    OpCode op;
    int reg;      // 0 для r1, 1 для r2
    int next_pc;  // Наступний крок
    int zero_pc;  // Крок при r == 0
} Instruction;

typedef struct {
    int pc;
    int64_t r1;
    int64_t r2;
} MachineState;

// Поліноміальна нев'язка переходу (повинна дорівнювати 0 для валідного кроку)
int64_t verify_diophantine_step(const Instruction* code, MachineState s_curr, MachineState s_next) {
    const Instruction* inst = &code[s_curr.pc];
    if (inst->op == OP_HALT) {
        return (s_next.pc - s_curr.pc) + (s_next.r1 - s_curr.r1) + (s_next.r2 - s_curr.r2);
    }
    if (inst->op == OP_INC) {
        int64_t r1_diff = (inst->reg == 0) ? (s_next.r1 - (s_curr.r1 + 1)) : (s_next.r1 - s_curr.r1);
        int64_t r2_diff = (inst->reg == 1) ? (s_next.r2 - (s_curr.r2 + 1)) : (s_next.r2 - s_curr.r2);
        int64_t pc_diff = s_next.pc - inst->next_pc;
        return r1_diff * r1_diff + r2_diff * r2_diff + pc_diff * pc_diff;
    }
    // OP_DEC_JNZ: розгалуження моделюється через добуток умов
    int64_t reg_val = (inst->reg == 0) ? s_curr.r1 : s_curr.r2;
    if (reg_val == 0) {
        int64_t pc_diff = s_next.pc - inst->zero_pc;
        int64_t r1_diff = s_next.r1 - s_curr.r1;
        int64_t r2_diff = s_next.r2 - s_curr.r2;
        return pc_diff * pc_diff + r1_diff * r1_diff + r2_diff * r2_diff;
    } else {
        int64_t pc_diff = s_next.pc - inst->next_pc;
        int64_t r1_diff = (inst->reg == 0) ? (s_next.r1 - (s_curr.r1 - 1)) : (s_next.r1 - s_curr.r1);
        int64_t r2_diff = (inst->reg == 1) ? (s_next.r2 - (s_curr.r2 - 1)) : (s_next.r2 - s_curr.r2);
        return pc_diff * pc_diff + r1_diff * r1_diff + r2_diff * r2_diff;
    }
}
