void cpu_interpret_threaded(CPUState *env, const uint8_t *guest_ram) {
    // Таблиця адрес міток-обробників інструкцій
    static const void *dispatch_table[256] = {
        [0x00] = &&op_nop,
        [0x01] = &&op_add,
        [0x02] = &&op_sub,
        [0xFF] = &&op_halt
    };

    #define DISPATCH() do {                                     \
        uint32_t instr = *(const uint32_t *)(guest_ram + env->pc); \
        env->pc += 4;                                           \
        uint8_t opcode = (instr >> 24) & 0xFF;                  \
        goto *dispatch_table[opcode];                           \
    } while (0)

    // Початковий запуск диспетчеризації
    DISPATCH();

op_add: {
    uint32_t instr = *(const uint32_t *)(guest_ram + env->pc - 4);
    uint8_t rd  = (instr >> 16) & 0x1F;
    uint8_t rs1 = (instr >> 11) & 0x1F;
    uint8_t rs2 = (instr >> 6)  & 0x1F;
    
    env->cc_op   = CC_OP_ADD;
    env->cc_src1 = env->regs[rs1];
    env->cc_src2 = env->regs[rs2];
    env->cc_dst  = env->cc_src1 + env->cc_src2;
    env->regs[rd] = env->cc_dst;
    
    DISPATCH();
}

op_sub: {
    uint32_t instr = *(const uint32_t *)(guest_ram + env->pc - 4);
    uint8_t rd  = (instr >> 16) & 0x1F;
    uint8_t rs1 = (instr >> 11) & 0x1F;
    uint8_t rs2 = (instr >> 6)  & 0x1F;
    
    env->cc_op   = CC_OP_SUB;
    env->cc_src1 = env->regs[rs1];
    env->cc_src2 = env->regs[rs2];
    env->cc_dst  = env->cc_src1 - env->cc_src2;
    env->regs[rd] = env->cc_dst;
    
    DISPATCH();
}

op_nop:
    DISPATCH();

op_halt:
    env->halted = true;
    return;
}
