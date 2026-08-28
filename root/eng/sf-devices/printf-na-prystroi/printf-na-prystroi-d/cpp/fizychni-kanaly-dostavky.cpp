#include <cstdint>

namespace itm_trace {
    inline volatile uint8_t& port0_u8() noexcept {
        return *reinterpret_cast<volatile uint8_t*>(0xE0000000UL);
    }
    inline volatile uint32_t& port0_u32() noexcept {
        return *reinterpret_cast<volatile uint32_t*>(0xE0000000UL);
    }
    inline volatile uint32_t& ter() noexcept {
        return *reinterpret_cast<volatile uint32_t*>(0xE0000E00UL);
    }
    inline volatile uint32_t& tcr() noexcept {
        return *reinterpret_cast<volatile uint32_t*>(0xE0000E80UL);
    }
    inline volatile uint32_t& demcr() noexcept {
        return *reinterpret_cast<volatile uint32_t*>(0xE000EDFCUL);
    }

    inline void send_char(uint8_t ch) noexcept {
        if ((demcr() & (1UL << 24)) && (tcr() & (1UL << 0)) && (ter() & (1UL << 0))) {
            while (port0_u32() == 0UL) {
                // Очікування готовності апаратного FIFO
            }
            port0_u8() = ch;
        }
    }
}
