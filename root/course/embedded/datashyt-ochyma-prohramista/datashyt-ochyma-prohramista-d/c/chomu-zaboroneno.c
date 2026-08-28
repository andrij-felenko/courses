/* Надійний патерн маніпуляції бітовими полями в C */
#define CTRL_ODR_POS       4
#define CTRL_ODR_MASK      (0x07 << CTRL_ODR_POS)
#define CTRL_ODR_100HZ     (0x03 << CTRL_ODR_POS)

#define CTRL_BDU_BIT       (1 << 3)
#define CTRL_ENABLE_BIT    (1 << 0)

uint8_t configure_reg(uint8_t current_val) {
    uint8_t val = current_val;
    val &= ~CTRL_ODR_MASK;      /* Очищаємо біти ODR */
    val |= CTRL_ODR_100HZ;      /* Встановлюємо нову частоту */
    val |= CTRL_BDU_BIT;        /* Вмикаємо BDU */
    val |= CTRL_ENABLE_BIT;     /* Активуємо чип */
    return val;
}
