#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <cstdint>
#include <iomanip>

enum class Opcode : uint8_t {
    Nop = 0x0,
    Add = 0x1,
    Sub = 0x2,
    And = 0x3,
    Or  = 0x4,
    Ldi = 0x5,
    Ld  = 0x6,
    St  = 0x7,
    Beq = 0x8,
    Hlt = 0xF
};

struct Flags {
    bool z{false};
    bool n{false};
    bool c{false};
    bool v{false};
};

class CpuCore {
public:
    static constexpr size_t RegCount = 8;
    static constexpr size_t MemSize = 256;

    CpuCore() {
        reset();
    }

    void reset() noexcept {
        registers_.fill(0);
        pc_ = 0;
        flags_ = Flags{};
        halted_ = false;
        program_mem_.fill(0);
        data_mem_.fill(0);
    }

    void load_program(std::span<const uint16_t> binary, uint16_t start_addr = 0) {
        for (size_t i = 0; i < binary.size() && (start_addr + i) < MemSize; ++i) {
            program_mem_[start_addr + i] = binary[i];
        }
        pc_ = start_addr;
        halted_ = false;
    }

    void step() {
        if (halted_) return;

        // 1. Fetch
        const uint16_t instr = program_mem_[pc_ % MemSize];
        pc_++;

        // 2. Decode
        const auto op   = static_cast<Opcode>((instr >> 12) & 0x0F);
        const uint8_t rd  = (instr >> 9) & 0x07;
        const uint8_t rs1 = (instr >> 6) & 0x07;
        const uint8_t rs2 = (instr >> 3) & 0x07;
        const uint16_t imm9 = instr & 0x01FF;

        // 3. Execute & Write-Back
        switch (op) {
            case Opcode::Nop:
                break;

            case Opcode::Add: {
                const uint32_t a = registers_[rs1];
                const uint32_t b = registers_[rs2];
                const uint32_t res = a + b;
                const auto res16 = static_cast<uint16_t>(res);

                if (rd != 0) registers_[rd] = res16;

                flags_.z = (res16 == 0);
                flags_.n = (res16 & 0x8000) != 0;
                flags_.c = (res > 0xFFFF);
                flags_.v = (!((a ^ b) & 0x8000) && ((a ^ res) & 0x8000));
                break;
            }

            case Opcode::Sub: {
                const uint32_t a = registers_[rs1];
                const uint32_t b = registers_[rs2];
                const uint32_t res = a - b;
                const auto res16 = static_cast<uint16_t>(res);

                if (rd != 0) registers_[rd] = res16;

                flags_.z = (res16 == 0);
                flags_.n = (res16 & 0x8000) != 0;
                flags_.c = (a >= b);
                flags_.v = (((a ^ b) & 0x8000) && ((a ^ res) & 0x8000));
                break;
            }

            case Opcode::And: {
                const uint16_t res = registers_[rs1] & registers_[rs2];
                if (rd != 0) registers_[rd] = res;
                flags_.z = (res == 0);
                flags_.n = (res & 0x8000) != 0;
                break;
            }

            case Opcode::Or: {
                const uint16_t res = registers_[rs1] | registers_[rs2];
                if (rd != 0) registers_[rd] = res;
                flags_.z = (res == 0);
                flags_.n = (res & 0x8000) != 0;
                break;
            }

            case Opcode::Ldi: {
                if (rd != 0) registers_[rd] = static_cast<uint16_t>(sign_extend_9(imm9));
                break;
            }

            case Opcode::Ld: {
                const size_t addr = registers_[rs1] % MemSize;
                if (rd != 0) registers_[rd] = data_mem_[addr];
                break;
            }

            case Opcode::St: {
                const size_t addr = registers_[rs1] % MemSize;
                data_mem_[addr] = registers_[rs2];
                break;
            }

            case Opcode::Beq: {
                if (registers_[rd] == registers_[rs1]) {
                    const int16_t offset = sign_extend_9(imm9);
                    pc_ = static_cast<uint16_t>(static_cast<int16_t>(pc_) + offset);
                }
                break;
            }

            case Opcode::Hlt:
                halted_ = true;
                break;

            default:
                halted_ = true;
                break;
        }

        registers_[0] = 0; // R0 завжди нульовий
    }

    [[nodiscard]] bool is_halted() const noexcept { return halted_; }
    [[nodiscard]] uint16_t reg(size_t idx) const noexcept { return registers_.at(idx); }
    [[nodiscard]] uint16_t pc() const noexcept { return pc_; }
    [[nodiscard]] const Flags& flags() const noexcept { return flags_; }
    [[nodiscard]] uint16_t read_data(size_t addr) const noexcept { return data_mem_.at(addr % MemSize); }

private:
    static constexpr int16_t sign_extend_9(uint16_t val) noexcept {
        if (val & 0x0100) {
            return static_cast<int16_t>(val | 0xFE00);
        }
        return static_cast<int16_t>(val & 0x01FF);
    }

    std::array<uint16_t, RegCount> registers_{};
    uint16_t pc_{0};
    Flags flags_{};
    bool halted_{false};
    std::array<uint16_t, MemSize> program_mem_{};
    std::array<uint16_t, MemSize> data_mem_{};
};
