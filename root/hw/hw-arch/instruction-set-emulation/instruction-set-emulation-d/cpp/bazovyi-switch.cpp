#include <span>

void cpu_interpret_loop_switch(CPUState& env, std::span<const uint8_t> guest_ram) {
    while (!env.halted) {
        // 1. Fetch: вибірка 32-бітної інструкції
        if (env.pc + 4 > guest_ram.size()) {
            env.halted = true;
            break;
        }
        
        uint32_t instr = *reinterpret_cast<const uint32_t*>(guest_ram.data() + env.pc);
        env.pc += 4;
        
        // 2. Decode: виділення опкоду та полів регістрів
        uint8_t opcode = (instr >> 24) & 0xFF;
        uint8_t rd     = (instr >> 16) & 0x1F;
        uint8_t rs1    = (instr >> 11) & 0x1F;
        uint8_t rs2    = (instr >> 6)  & 0x1F;
        
        // 3. Execute: диспетчеризація
        switch (opcode) {
            case 0x01: // ADD
                env.cc_op   = static_cast<uint32_t>(CCOperation::Add);
                env.cc_src1 = env.regs[rs1];
                env.cc_src2 = env.regs[rs2];
                env.cc_dst  = env.cc_src1 + env.cc_src2;
                env.regs[rd] = env.cc_dst;
                break;
                
            case 0x02: // SUB
                env.cc_op   = static_cast<uint32_t>(CCOperation::Sub);
                env.cc_src1 = env.regs[rs1];
                env.cc_src2 = env.regs[rs2];
                env.cc_dst  = env.cc_src1 - env.cc_src2;
                env.regs[rd] = env.cc_dst;
                break;
                
            case 0xFF: // HALT
                env.halted = true;
                break;
                
            default:
                env.halted = true;
                break;
        }
    }
}
