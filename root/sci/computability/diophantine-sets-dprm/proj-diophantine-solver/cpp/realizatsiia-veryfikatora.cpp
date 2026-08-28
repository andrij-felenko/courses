#include <vector>
#include <cstdint>

enum class OpCode { Inc, DecJnz, Halt };

struct Instruction {
    OpCode op{OpCode::Halt};
    int reg{0};      // 0 -> r1, 1 -> r2
    int next_pc{0};
    int zero_pc{0};
};

struct MachineState {
    int pc{0};
    int64_t r1{0};
    int64_t r2{0};
};

class MinskyVerifier {
public:
    static int64_t verify_step(const std::vector<Instruction>& code, 
                               MachineState s_curr, MachineState s_next) noexcept {
        const auto& inst = code[s_curr.pc];
        if (inst.op == OpCode::Halt) {
            return (s_next.pc - s_curr.pc) + (s_next.r1 - s_curr.r1) + (s_next.r2 - s_curr.r2);
        }
        if (inst.op == OpCode::Inc) {
            const int64_t r1_diff = (inst.reg == 0) ? (s_next.r1 - (s_curr.r1 + 1)) : (s_next.r1 - s_curr.r1);
            const int64_t r2_diff = (inst.reg == 1) ? (s_next.r2 - (s_curr.r2 + 1)) : (s_next.r2 - s_curr.r2);
            const int64_t pc_diff = s_next.pc - inst.next_pc;
            return r1_diff * r1_diff + r2_diff * r2_diff + pc_diff * pc_diff;
        }

        const int64_t reg_val = (inst.reg == 0) ? s_curr.r1 : s_curr.r2;
        if (reg_val == 0) {
            const int64_t pc_diff = s_next.pc - inst.zero_pc;
            const int64_t r1_diff = s_next.r1 - s_curr.r1;
            const int64_t r2_diff = s_next.r2 - s_curr.r2;
            return pc_diff * pc_diff + r1_diff * r1_diff + r2_diff * r2_diff;
        } else {
            const int64_t pc_diff = s_next.pc - inst.next_pc;
            const int64_t r1_diff = (inst.reg == 0) ? (s_next.r1 - (s_curr.r1 - 1)) : (s_next.r1 - s_curr.r1);
            const int64_t r2_diff = (inst.reg == 1) ? (s_next.r2 - (s_curr.r2 - 1)) : (s_next.r2 - s_curr.r2);
            return pc_diff * pc_diff + r1_diff * r1_diff + r2_diff * r2_diff;
        }
    }
};
