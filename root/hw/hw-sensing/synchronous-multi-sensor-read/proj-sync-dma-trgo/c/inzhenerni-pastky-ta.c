/* Програмне розблокування лінії SDA шини I2C */
void i2c_bus_unlock_recovery(GPIO_TypeDef* port, uint16_t scl_pin, uint16_t sda_pin) {
    /* Генеруємо 9 тактів на SCL при відпущеній лінії SDA */
    for (int i = 0; i < 9; i++) {
        port->BSRR = (1U << (scl_pin + 16)); /* SCL = LOW */
        for (volatile int d = 0; d < 50; d++);
        port->BSRR = (1U << scl_pin);        /* SCL = HIGH */
        for (volatile int d = 0; d < 50; d++);
    }
}
