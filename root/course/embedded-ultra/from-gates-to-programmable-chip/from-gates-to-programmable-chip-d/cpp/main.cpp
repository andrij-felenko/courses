#include <cstdint>
#include <array>
#include <span>

struct StatusFlags {
    bool zero{false};
    bool negative{false};
    bool carry{false};
    bool overflow{false};
};

class Core16 {
public:
    static constexpr size_t RegisterCount = 8;
    static constexpr size_t MemorySize = 256;

    void step() {
        if (halted_) return;

        // 1. Fetch
        const uint16_t instr = rom_[pc_++];

        // 2. Decode
        const uint8_t op  = (instr >> 12) & 0x0F;
        const uint8_t rd  = (instr >> 9)  & 0x07;
        const uint8_t rs1 = (instr >> 6)  & 0x07;
        const uint8_t rs2 = (instr >> 3)  & 0x07;

        // 3. Execute / Write-back
        if (op == 0x1) { // ADD Rd, Rs1, Rs2
            const uint32_t a = registers_[rs1];
            const uint32_t b = registers_[rs2];
            const uint32_t sum = a + b;
            const auto res = static_cast<uint16_t>(sum);

            if (rd != 0) registers_[rd] = res;

            flags_.zero = (res == 0);
            flags_.negative = (res & 0x8000) != 0;
            flags_.carry = (sum > 0xFFFF);
            flags_.overflow = (!((a ^ b) & 0x8000) && ((a ^ sum) & 0x8000));
        } else if (op == 0xF) { // HLT
            halted_ = true;
        }

        registers_[0] = 0; // R0 жорстко нульовий
    }

    [[nodiscard]] uint16_t read_reg(size_t index) const noexcept {
        return registers_.at(index);
    }

private:
    std::array<uint16_t, RegisterCount> registers_{};
    uint16_t pc_{0};
    StatusFlags flags_{};
    bool halted_{false};
    std::array<uint16_t, MemorySize> rom_{};
    std::array<uint16_t, MemorySize> ram_{};
};
