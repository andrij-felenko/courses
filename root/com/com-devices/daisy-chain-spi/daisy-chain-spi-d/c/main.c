#include <stdint.h>
#include <stdbool.h>

#define CHAIN_LENGTH  4   /* 4 мікросхеми в каскаді */

/* Прототипи апаратних функцій HAL */
extern void hal_gpio_write_cs(bool level);
extern void hal_spi_transmit_receive(const uint8_t *tx, uint8_t *rx, uint16_t len);

/* Відправка 16-бітних слів на 4 каскадні мікросхеми */
void daisy_chain_update_4x16(const uint16_t values[CHAIN_LENGTH], uint16_t feedback[CHAIN_LENGTH]) {
    uint8_t tx_buf[CHAIN_LENGTH * 2];
    uint8_t rx_buf[CHAIN_LENGTH * 2];

    /* Пакування слів у передавальний буфер у ЗВОРОТНОМУ порядку:
       Слово для IC4 передається першим, слово для IC1 — останнім */
    for (int i = 0; i < CHAIN_LENGTH; ++i) {
        int rev_index = (CHAIN_LENGTH - 1) - i;
        uint16_t word = values[rev_index];
        tx_buf[i * 2 + 0] = (uint8_t)(word >> 8);    /* Старший байт (MSB) */
        tx_buf[i * 2 + 1] = (uint8_t)(word & 0xFF);   /* Молодший байт (LSB) */
    }

    /* Початок кадру: активний рівень CS */
    hal_gpio_write_cs(false);

    /* Апаратна повнодуплексна передача 8 байтів */
    hal_spi_transmit_receive(tx_buf, rx_buf, sizeof(tx_buf));

    /* Кінець кадру: наростаючий фронт CS фіксує дані у засувках (Latch) */
    hal_gpio_write_cs(true);

    /* Розпакування зчитаних даних зі зворотного потоку */
    for (int i = 0; i < CHAIN_LENGTH; ++i) {
        int rev_index = (CHAIN_LENGTH - 1) - i;
        uint16_t hi = rx_buf[i * 2 + 0];
        uint16_t lo = rx_buf[i * 2 + 1];
        feedback[rev_index] = (uint16_t)((hi << 8) | lo);
    }
}
