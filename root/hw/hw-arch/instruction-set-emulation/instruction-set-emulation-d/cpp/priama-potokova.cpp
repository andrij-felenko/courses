#include <array>
#include <span>

// У C++ стандарті без розширень компілятора пряма потокова диспетчеризація
// емулюється через масив покажчиків на функції-обробники:
using OpcodeHandler = void (*)(CPUState&, uint32_t);

void handler_add(CPUState& env, uint32_t instr) noexcept {
    uint8_t rd  = (instr >> 16) & 0x1F;
    uint8_t rs1 = (instr >> 11) & 0x1F;
    uint8_t rs2 = (instr >> 6)  & 0x1F;
    
    env.cc_op   = static_cast<uint32_t>(CCOperation::Add);
    env.cc_src1 = env.regs[rs1];
    env.cc_src2 = env.regs[rs2];
    env.cc_dst  = env.cc_src1 + env.cc_src2;
    env.regs[rd] = env.cc_dst;
}

void handler_sub(CPUState& env, uint32_t instr) noexcept {
    uint8_t rd  = (instr >> 16) & 0x1F;
    uint8_t rs1 = (instr >> 11) & 0x1F;
    uint8_t rs2 = (instr >> 6)  & 0x1F;
    
    env.cc_op   = static_cast<uint32_t>(CCOperation::Sub);
    env.cc_src1 = env.regs[rs1];
    env.cc_src2 = env.regs[rs2];
    env.cc_dst  = env.cc_src1 - env.cc_src2;
    env.regs[rd] = env.cc_dst;
}

void handler_halt(CPUState& env, uint32_t) noexcept {
    env.halted = true;
}

void cpu_interpret_function_table(CPUState& env, std::span<const uint8_t> guest_ram) {
    static constexpr std::array<OpcodeHandler, 256> Table = []() constexpr {
        std::array<OpcodeHandler, 256> t{};
        t[0x01] = &handler_add;
        t[0x02] = &handler_sub;
        t[0xFF] = &handler_halt;
        return t;
    }();

    while (!env.halted) {
        uint32_t instr = *reinterpret_cast<const uint32_t*>(guest_ram.data() + env.pc);
        env.pc += 4;
        uint8_t opcode = (instr >> 24) & 0xFF;
        
        OpcodeHandler handler = Table[opcode];
        if (handler) {
            handler(env, instr);
        } else {
            env.halted = true;
        }
    }
}
