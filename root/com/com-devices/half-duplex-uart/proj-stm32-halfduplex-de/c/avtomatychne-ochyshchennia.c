// Обробка та очищення прапорців помилок UART (STM32, C)
static inline void usart1_clear_error_flags(uint32_t isr) {
    uint32_t clear_mask = 0;
    if (isr & USART_ISR_ORE) clear_mask |= USART_ICR_ORECF;
    if (isr & USART_ISR_FE)  clear_mask |= USART_ICR_FECF;
    if (isr & USART_ISR_NE)  clear_mask |= USART_ICR_NECF;
    if (isr & USART_ISR_PE)  clear_mask |= USART_ICR_PECF;
    if (clear_mask != 0) {
        USART1->ICR = clear_mask;
    }
}
