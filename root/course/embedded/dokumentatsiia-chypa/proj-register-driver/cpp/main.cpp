#include <cstdint>
#include <cstddef>
#include <concepts>
#include <span>

namespace hardware {

/* Структура регістрової карти USART за Reference Manual */
struct UsartBlock {
    volatile uint32_t cr1;    // 0x00: Control Register 1
    volatile uint32_t cr2;    // 0x04: Control Register 2
    volatile uint32_t cr3;    // 0x08: Control Register 3
    volatile uint32_t brr;    // 0x0C: Baud Rate Register
    volatile uint32_t gtpr;   // 0x10: Guard Time / Prescaler
    volatile uint32_t rtor;   // 0x14: Receiver Timeout
    volatile uint32_t rqr;    // 0x18: Request Register
    volatile uint32_t isr;    // 0x1C: Status & Interrupts (RO / W1C)
    volatile uint32_t icr;    // 0x20: Flag Clear (Write 1 to Clear)
    volatile uint32_t rdr;    // 0x24: Receive Data Register
    volatile uint32_t tdr;    // 0x28: Transmit Data Register
};

struct DbgMcuBlock {
    volatile uint32_t idcode; // 0x00: Device ID & Revision
};

/* Типобезпечні константи адрес та масок */
inline constexpr uintptr_t usart1_address = 0x40013800UL;
inline constexpr uintptr_t dbgmcu_address = 0xE0042000UL;

namespace flags {
    inline constexpr uint32_t cr1_ue   = 1UL << 0;
    inline constexpr uint32_t cr1_te   = 1UL << 3;
    inline constexpr uint32_t isr_txe  = 1UL << 7;
    inline constexpr uint32_t isr_tc   = 1UL << 6;
    inline constexpr uint32_t icr_tccf = 1UL << 6;
}

/* Інкапсульований драйвер UART із захистом від апаратних пасток */
class UartDriver {
public:
    explicit constexpr UartDriver(uintptr_t base_addr = usart1_address) noexcept
        : regs_(*reinterpret_cast<UsartBlock*>(base_addr)),
          dbg_(*reinterpret_cast<DbgMcuBlock*>(dbgmcu_address)) {}

    // Заборона копіювання: апаратний блок унікальний
    UartDriver(const UartDriver&) = delete;
    UartDriver& operator=(const UartDriver&) = delete;

    [[nodiscard]] uint16_t get_silicon_revision() const noexcept {
        return static_cast<uint16_t>(dbg_.idcode >> 16);
    }

    void init_transmitter(uint32_t bus_clock_hz, uint32_t baudrate) noexcept {
        const uint32_t brr_val = (bus_clock_hz + (baudrate / 2U)) / baudrate;
        regs_.brr = brr_val;
        regs_.cr1 = flags::cr1_ue | flags::cr1_te;

        // Errata Workaround: затримка на 1 такт для ревізії Rev A (0x1000)
        if (get_silicon_revision() == 0x1000U) {
            asm volatile("nop");
        }
    }

    [[nodiscard]] bool send_byte(uint8_t byte, uint32_t timeout_cycles = 100'000) noexcept {
        while ((regs_.isr & flags::isr_txe) == 0) {
            if (timeout_cycles == 0) {
                return false;
            }
            --timeout_cycles;
        }

        regs_.tdr = byte;
        return true;
    }

    size_t send_buffer(std::span<const uint8_t> data) noexcept {
        size_t sent = 0;
        for (uint8_t byte : data) {
            if (!send_byte(byte)) {
                break;
            }
            ++sent;
        }
        return sent;
    }

    void clear_transmission_complete_flag() noexcept {
        // Атомарне очищення W1C: запис у ICR без модифікації ISR
        regs_.icr = flags::icr_tccf;
    }

private:
    UsartBlock& regs_;
    DbgMcuBlock& dbg_;
};

} // namespace hardware
