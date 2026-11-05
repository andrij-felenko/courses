#include <cstdint>
#include <array>

constexpr size_t VM_STACK_DEPTH = 4;
constexpr size_t VM_NUM_REGS    = 4;

enum class VMStatus : uint8_t {
    Idle = 0,
    Running,
    Waiting,
    Halted,
    ErrorStackOverflow,
    ErrorStackUnderflow,
    ErrorInvalidOpcode
};

class MicroVMContext {
public:
    uint16_t ip{0};
    std::array<uint16_t, VM_NUM_REGS> registers{0};
    uint32_t delay_until_ms{0};
    std::array<uint16_t, VM_STACK_DEPTH> stack{0};
    uint8_t sp{0};
    VMStatus status{VMStatus::Idle};
    const uint8_t* code{nullptr};
    uint16_t code_len{0};

    constexpr MicroVMContext() = default;

    void init(const uint8_t* bytecode, uint16_t length) noexcept {
        ip = 0;
        registers.fill(0);
        delay_until_ms = 0;
        stack.fill(0);
        sp = 0;
        status = VMStatus::Idle;
        code = bytecode;
        code_len = length;
    }
};
