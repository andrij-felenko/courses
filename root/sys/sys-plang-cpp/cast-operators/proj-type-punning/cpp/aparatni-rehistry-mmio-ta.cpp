#include <cstdint>
#include <span>

struct UartRegisters {
    volatile uint32_t cr1;
    volatile uint32_t cr2;
    volatile uint32_t sr;
    volatile uint32_t dr;
};

// Безпечне зв'язування апаратної адреси у C++
class UartDriver {
public:
    explicit constexpr UartDriver(uintptr_t base_addr) noexcept
        : regs_(reinterpret_cast<UartRegisters*>(base_addr)) {}

    void send_byte(uint8_t byte) const noexcept {
        // Очікування прапорця TXE (Transmit data register empty)
        while ((regs_->sr & 0x00000080u) == 0) {
            // Апаратне очікування
        }
        regs_->dr = byte;
    }

private:
    UartRegisters* const regs_;
};
