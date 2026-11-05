uint8_t hc165_read(void) {
    uint8_t result = 0;
    
    // 1. Захоплення паралельних входів
    HAL_GPIO_WritePin(PORT_SH_LD, PIN_SH_LD, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(PORT_SH_LD, PIN_SH_LD, GPIO_PIN_SET);
    
    // 2. Послідовне зчитування
    for (int i = 0; i < 8; i++) {
        // Читаємо біт, що вже стоїть на лінії (першим іде старший розряд H)
        uint8_t bit = HAL_GPIO_ReadPin(PORT_QH, PIN_QH);
        result |= (bit << (7 - i));
        
        // Генеруємо імпульс для зсуву наступного біта
        HAL_GPIO_WritePin(PORT_CLK, PIN_CLK, GPIO_PIN_SET);
        HAL_GPIO_WritePin(PORT_CLK, PIN_CLK, GPIO_PIN_RESET);
    }
    
    return result;
}
