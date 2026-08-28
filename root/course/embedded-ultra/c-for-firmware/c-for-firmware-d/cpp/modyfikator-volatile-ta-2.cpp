#include <cstdint>
#include <span>

// Ідіоматичний C++ доступ до апаратної периферії через типізовані структури
struct UartRegs {
    volatile uint32_t sr;
    volatile uint32_t dr;
    volatile uint32_t brr;
    volatile uint32_t cr1;
    volatile uint32_t cr2;
    volatile uint32_t cr3;
};

inline auto uart1 = reinterpret_cast<UartRegs*>(0x40013800UL);

class UartDriver {
public:
    constexpr explicit UartDriver(UartRegs* regs) noexcept : regs_(regs) {}

    void send_byte(uint8_t byte) noexcept {
        constexpr uint32_t txe_bit = 1U << 7;
        while (!(regs_->sr & txe_bit)) {
            // Очікування звільнення вихідного буфера
        }
        regs_->dr = byte;
    }

    void write(std::span<const uint8_t> data) noexcept {
        for (uint8_t byte : data) {
            send_byte(byte);
        }
    }

private:
    UartRegs* regs_;
};
