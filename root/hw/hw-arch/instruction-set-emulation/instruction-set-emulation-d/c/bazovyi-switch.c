void cpu_interpret_loop_switch(CPUState *env, const uint8_t *guest_ram) {
    while (!env->halted) {
        // 1. Fetch: вибірка 32-бітної інструкції
        uint32_t instr = *(const uint32_t *)(guest_ram + env->pc);
        env->pc += 4;
        
        // 2. Decode: виділення опкоду (старші 8 біт)
        uint8_t opcode = (instr >> 24) & 0xFF;
        uint8_t rd     = (instr >> 16) & 0x1F;
        uint8_t rs1    = (instr >> 11) & 0x1F;
        uint8_t rs2    = (instr >> 6)  & 0x1F;
        
        // 3. Execute: диспетчеризація через switch
        switch (opcode) {
            case 0x01: // ADD rd, rs1, rs2
                env->cc_op   = CC_OP_ADD;
                env->cc_src1 = env->regs[rs1];
                env->cc_src2 = env->regs[rs2];
                env->cc_dst  = env->cc_src1 + env->cc_src2;
                env->regs[rd] = env->cc_dst;
                break;
                
            case 0x02: // SUB rd, rs1, rs2
                env->cc_op   = CC_OP_SUB;
                env->cc_src1 = env->regs[rs1];
                env->cc_src2 = env->regs[rs2];
                env->cc_dst  = env->cc_src1 - env->cc_src2;
                env->regs[rd] = env->cc_dst;
                break;
                
            case 0xFF: // HALT
                env->halted = true;
                break;
                
            default:
                // Невідома інструкція — аварійна зупинка
                env->halted = true;
                break;
        }
    }
}
