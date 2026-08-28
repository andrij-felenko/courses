/* ЖАХЛИВИЙ АНТИПАТЕРН: активне очікування всередині ISR на C++ */
extern "C" void USART1_IRQHandler() {
    if ((USART1->SR & USART_SR_RXNE) != 0) {
        const uint8_t data = static_cast<uint8_t>(USART1->DR);
        
        /* Заборонено! Блокуючий цикл очікування апаратури */
        while ((I2C1->SR1 & I2C_SR1_TXE) == 0) {
            // Безкінечний цикл у разі апаратного збою шини
        }
        I2C1->DR = data;
    }
}
