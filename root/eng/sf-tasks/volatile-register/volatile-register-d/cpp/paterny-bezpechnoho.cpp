#include <cstdint>
#include <cstddef>

// Оголошення структури регістрів для C++
struct USART_TypeDef {
    volatile std::uint32_t CR1;        // +0x00: RW
    volatile std::uint32_t CR2;        // +0x04: RW
    const volatile std::uint32_t SR;   // +0x08: RO (Захист від запису компілятором)
    std::uint32_t RESERVED[2];         // +0x0C .. +0x10: Відступ
    volatile std::uint32_t DR;         // +0x14: RW
};

inline constexpr std::uintptr_t USART1_BASE = 0x40013800UL;

// Отримання посилання на апаратний модуль
inline USART_TypeDef& get_usart1() noexcept {
    return *reinterpret_cast<USART_TypeDef*>(USART1_BASE);
}

void usart_send_byte(USART_TypeDef &usart, std::uint8_t byte) noexcept {
    constexpr std::uint32_t TXE_BIT = 1U << 7;
    while (!(usart->SR & TXE_BIT)) {
        // Опитування згенеровано коректно через volatile-семантику
    }
    usart->DR = byte;
}
