#define BIT_US (1000000UL / 9600UL)   /* 104 мкс на біт при 9600 бод */

void uart_tx_byte(uint8_t b) {
    gpio_write(TX_PIN, 0);            /* старт-біт: лінія йде в «0» */
    delay_us(BIT_US);
    for (uint8_t i = 0; i < 8; i++) { /* 8 біт даних, молодший уперед */
        gpio_write(TX_PIN, b & 1);
        delay_us(BIT_US);
        b >>= 1;
    }
    gpio_write(TX_PIN, 1);            /* стоп-біт: лінія назад у спокій «1» */
    delay_us(BIT_US);
}
