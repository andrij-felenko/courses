#include <cstdint>
#include <array>

enum class Opcode : uint8_t {
    Nop      = 0x00,
    SetGpio  = 0x01,
    ReadAdc  = 0x02,
    Jmp      = 0x03,
    Call     = 0x04,
    Ret      = 0x05,
    WaitMs   = 0x06,
    Yield    = 0x07,
    Halt     = 0xFF
};

template <size_t StackDepth = 8, size_t RegCount = 4>
class BytecodeVm {
public:
    struct State {
        uint16_t ip{0};
        uint8_t sp{0};
        std::array<uint16_t, StackDepth> stack{};
        std::array<uint16_t, RegCount> regs{};
        uint32_t wait_until_ms{0};
        bool is_running{false};
        bool is_waiting{false};
    };

    explicit BytecodeVm(const uint8_t* code_ptr, size_t size) 
        : code_(code_ptr), code_size_(size) {
        state_.is_running = true;
    }

    bool step(uint32_t current_ms) {
        if (!state_.is_running) return false;

        if (state_.is_waiting) {
            if (current_ms >= state_.wait_until_ms) {
                state_.is_waiting = false;
            } else {
                return true;
            }
        }

        if (state_.ip >= code_size_) {
            state_.is_running = false;
            return false;
        }

        auto op = static_cast<Opcode>(fetch_byte());

        switch (op) {
            case Opcode::Nop:
                break;

            case Opcode::SetGpio: {
                uint8_t pin = fetch_byte();
                uint8_t val = fetch_byte();
                execute_set_gpio(pin, val);
                break;
            }

            case Opcode::WaitMs: {
                uint16_t delay = fetch_word();
                state_.wait_until_ms = current_ms + delay;
                state_.is_waiting = true;
                break;
            }

            case Opcode::Jmp: {
                uint16_t target = fetch_word();
                if (target >= code_size_) { state_.is_running = false; return false; }
                state_.ip = target;
                break;
            }

            case Opcode::Call: {
                uint16_t target = fetch_word();
                if (state_.sp >= StackDepth || target >= code_size_) {
                    state_.is_running = false;
                    return false;
                }
                state_.stack[state_.sp++] = state_.ip;
                state_.ip = target;
                break;
            }

            case Opcode::Ret: {
                if (state_.sp == 0) {
                    state_.is_running = false;
                    return false;
                }
                state_.ip = state_.stack[--state_.sp];
                break;
            }

            case Opcode::Yield:
                return true;

            case Opcode::Halt:
                state_.is_running = false;
                return false;

            default:
                state_.is_running = false;
                return false;
        }

        return true;
    }

    const State& get_state() const { return state_; }

private:
    const uint8_t* code_;
    size_t code_size_;
    State state_;

    uint8_t fetch_byte() { return code_[state_.ip++]; }
    
    uint16_t fetch_word() {
        uint16_t val = static_cast<uint16_t>(code_[state_.ip]) | 
                      (static_cast<uint16_t>(code_[state_.ip + 1]) << 8);
        state_.ip += 2;
        return val;
    }

    void execute_set_gpio(uint8_t pin, uint8_t val) {
        (void)pin; (void)val;
    }
};
