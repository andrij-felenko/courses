// Обробка та очищення прапорців помилок UART (C++)
#include <cstdint>

struct HardwareErrorManager {
    static inline void clear_if_present(std::uint32_t isr_status) noexcept {
        std::uint32_t clear_mask = 0;
        if (isr_status & USART_ISR_ORE) clear_mask |= USART_ICR_ORECF;
        if (isr_status & USART_ISR_FE)  clear_mask |= USART_ICR_FECF;
        if (isr_status & USART_ISR_NE)  clear_mask |= USART_ICR_NECF;
        if (isr_status & USART_ISR_PE)  clear_mask |= USART_ICR_PECF;
        if (clear_mask != 0) {
            USART1->ICR = clear_mask;
        }
    }
};
