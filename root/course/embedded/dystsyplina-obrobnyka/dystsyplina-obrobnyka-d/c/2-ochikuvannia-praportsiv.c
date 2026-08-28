/* ЖАХЛИВИЙ АНТИПАТЕРН: активне очікування всередині ISR */
void USART1_IRQHandler(void) {
    if (USART1->SR & USART_SR_RXNE) {
        uint8_t data = USART1->DR;
        
        /* Заборонено! Очікування готовності передавача I2C або SPI */
        while (!(I2C1->SR1 & I2C_SR1_TXE)) {
            /* Якщо шина I2C зависла через шум на лінії SCL,
               ми заблокуємо всі переривання назавжди! */
        }
        I2C1->DR = data;
    }
}
