#include <cstdint>

struct UsartRegisters {
    volatile uint32_t sr;
    volatile uint32_t dr;
    volatile uint32_t brr;
    volatile uint32_t cr1;
    volatile uint32_t cr2;
    volatile uint32_t cr3;
    volatile uint32_t gtpr;
};

inline constexpr uintptr_t usart1_base_addr = 0x40013800UL;
inline constexpr uintptr_t usart2_base_addr = 0x40004400UL;

inline auto* const Usart1 = reinterpret_cast<UsartRegisters*>(usart1_base_addr);
inline auto* const Usart2 = reinterpret_cast<UsartRegisters*>(usart2_base_addr);
