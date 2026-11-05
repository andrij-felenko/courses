#include <cstdint>
#include <array>

extern "C" uint32_t sys_now_ms();
extern "C" void hal_gpio_write(uint8_t pin, uint8_t val);

class BytecodeVm {
public:
    static constexpr std::size_t StackDepth = 8;
    static constexpr std::size_t NumRegisters = 4;

    enum class Status : uint8_t {
        Idle = 0,
        Running,
        Waiting,
        ErrorInvalidOpcode,
        ErrorStackOverflow,
        ErrorStackUnderflow,
        ErrorOutOfBounds
    };

    enum class Opcode : uint8_t {
        Nop     = 0x00,
        Jmp     = 0x01,
        Call    = 0x03,
        Ret     = 0x04,
        Yield   = 0x05,
        Wait    = 0x06,
        GpioSet = 0x10
    };

    BytecodeVm() = default;

    void load(const uint8_t* code_ptr, uint16_t size) {
        code_ = code_ptr;
        code_size_ = size;
        ip_ = 0;
        sp_ = 0;
        wait_until_ms_ = 0;
        status_ = Status::Running;
        registers_.fill(0);
    }

    Status step() {
        if (status_ == Status::Waiting) {
            if (sys_now_ms() >= wait_until_ms_) {
                status_ = Status::Running;
            } else {
                return status_;
            }
        }

        if (status_ != Status::Running) {
            return status_;
        }

        if (ip_ >= code_size_) {
            status_ = Status::ErrorOutOfBounds;
            return status_;
        }

        auto opcode = static_cast<Opcode>(code_[ip_++]);

        switch (opcode) {
            case Opcode::Nop:
                break;

            case Opcode::Jmp: {
                if (ip_ + 2 > code_size_) {
                    status_ = Status::ErrorOutOfBounds;
                    break;
                }
                uint16_t target = code_[ip_] | (static_cast<uint16_t>(code_[ip_ + 1]) << 8);
                ip_ = target;
                break;
            }

            case Opcode::Call: {
                if (ip_ + 2 > code_size_) {
                    status_ = Status::ErrorOutOfBounds;
                    break;
                }
                if (sp_ >= StackDepth) {
                    status_ = Status::ErrorStackOverflow;
                    break;
                }
                uint16_t target = code_[ip_] | (static_cast<uint16_t>(code_[ip_ + 1]) << 8);
                stack_[sp_++] = ip_ + 2;
                ip_ = target;
                break;
            }

            case Opcode::Ret: {
                if (sp_ == 0) {
                    status_ = Status::ErrorStackUnderflow;
                    break;
                }
                ip_ = stack_[--sp_];
                break;
            }

            case Opcode::Yield:
                return Status::Waiting;

            case Opcode::Wait: {
                if (ip_ + 2 > code_size_) {
                    status_ = Status::ErrorOutOfBounds;
                    break;
                }
                uint16_t delay_ms = code_[ip_] | (static_cast<uint16_t>(code_[ip_ + 1]) << 8);
                ip_ += 2;
                wait_until_ms_ = sys_now_ms() + delay_ms;
                status_ = Status::Waiting;
                break;
            }

            case Opcode::GpioSet: {
                if (ip_ + 2 > code_size_) {
                    status_ = Status::ErrorOutOfBounds;
                    break;
                }
                uint8_t pin = code_[ip_++];
                uint8_t val = code_[ip_++];
                hal_gpio_write(pin, val);
                break;
            }

            default:
                status_ = Status::ErrorInvalidOpcode;
                break;
        }

        return status_;
    }

    [[nodiscard]] Status get_status() const { return status_; }

private:
    const uint8_t* code_{nullptr};
    uint16_t code_size_{0};
    uint16_t ip_{0};
    uint8_t sp_{0};
    std::array<uint16_t, StackDepth> stack_{};
    std::array<int32_t, NumRegisters> registers_{};
    uint32_t wait_until_ms_{0};
    Status status_{Status::Idle};
};
