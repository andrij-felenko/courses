#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

bool read_w25q128_jedec_id(const spi_bitbang_t *bus, uint8_t *manuf_id, uint16_t *device_id) {
    uint8_t tx_cmd[4] = {0x9F, 0xFF, 0xFF, 0xFF};
    uint8_t rx_resp[4] = {0};

    spi_bb_transfer_buffer(bus, tx_cmd, rx_resp, 4);

    *manuf_id = rx_resp[1];
    *device_id = ((uint16_t)rx_resp[2] << 8) | rx_resp[3];

    /* Перевірка коду виробника Winbond (0xEF) */
    return (*manuf_id == 0xEF);
}
