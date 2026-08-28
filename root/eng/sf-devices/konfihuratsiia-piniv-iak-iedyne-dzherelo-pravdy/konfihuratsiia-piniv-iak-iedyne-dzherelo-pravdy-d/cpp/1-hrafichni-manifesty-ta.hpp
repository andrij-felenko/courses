namespace bsp {

struct PinInitDef {
    uint32_t pin;
    uint32_t mode;
    uint32_t pull;
    uint32_t speed;
    uint32_t alternate;
};

inline void init_hardware_pins() noexcept {
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();

    constexpr PinInitDef uart_cfg{
        .pin = GPIO_PIN_9 | GPIO_PIN_10,
        .mode = GPIO_MODE_AF_PP,
        .pull = GPIO_NOPULL,
        .speed = GPIO_SPEED_FREQ_VERY_HIGH,
        .alternate = GPIO_AF7_USART1
    };

    GPIO_InitTypeDef init_struct{};
    init_struct.Pin = uart_cfg.pin;
    init_struct.Mode = uart_cfg.mode;
    init_struct.Pull = uart_cfg.pull;
    init_struct.Speed = uart_cfg.speed;
    init_struct.Alternate = uart_cfg.alternate;
    HAL_GPIO_Init(GPIOA, &init_struct);

    constexpr PinInitDef i2c_cfg{
        .pin = GPIO_PIN_6 | GPIO_PIN_7,
        .mode = GPIO_MODE_AF_OD,
        .pull = GPIO_PULLUP,
        .speed = GPIO_SPEED_FREQ_HIGH,
        .alternate = GPIO_AF4_I2C1
    };

    init_struct.Pin = i2c_cfg.pin;
    init_struct.Mode = i2c_cfg.mode;
    init_struct.Pull = i2c_cfg.pull;
    init_struct.Speed = i2c_cfg.speed;
    init_struct.Alternate = i2c_cfg.alternate;
    HAL_GPIO_Init(GPIOB, &init_struct);
}

} // namespace bsp
