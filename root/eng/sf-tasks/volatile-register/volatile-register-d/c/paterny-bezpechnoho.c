#include <stdint.h>

// Оголошення структури регістрів периферійного модуля
typedef struct {
    volatile uint32_t CR1;        // +0x00: Регістр керування 1 (Читання/Запис, RW)
    volatile uint32_t CR2;        // +0x04: Регістр керування 2 (Читання/Запис, RW)
    const volatile uint32_t SR;   // +0x08: Регістр статусу (Тільки читання, RO)
    uint32_t RESERVED[2];         // +0x0C .. +0x10: Нереалізований адресний простір
    volatile uint32_t DR;         // +0x14: Регістр даних (Читання/Запис, RW)
} USART_TypeDef;

// Фіксація базової адреси периферійного блоку в пам'яті
#define USART1_BASE  (0x40013800UL)
#define USART1       ((USART_TypeDef *)USART1_BASE)

// Функція передачі байта
void usart_send_byte(USART_TypeDef *usart, uint8_t byte) {
    // Очікування встановлення біта TXE (Transmit Data Register Empty)
    while (!(usart->SR & (1U << 7))) {
        // Опитування статусу через const volatile uint32_t
    }
    // Запис байта в регістр даних
    usart->DR = byte;
}
