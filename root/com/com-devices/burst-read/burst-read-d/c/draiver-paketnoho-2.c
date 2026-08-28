#include <stdint.h>
#include <stdbool.h>
#include <string.h>

extern void platform_spi_cs_low(void);
extern void platform_spi_cs_high(void);
extern bool platform_spi_transfer(const uint8_t *tx, uint8_t *rx, size_t len);

typedef struct {
    int16_t gyro[3];
    int16_t accel[3];
} imu_6axis_raw_t;

/* Читання 12 байтів (Гіроскоп 0x22..0x27 + Акселерометр 0x28..0x2D) по SPI */
bool lsm6dso_spi_read_motion(imu_6axis_raw_t *out_data) {
    if (out_data == NULL) {
        return false;
    }

    /* Командний байт: Біт 7=1 (Read), адреса 0x22 (OUTX_L_G) */
    uint8_t tx_buf[13] = {0};
    uint8_t rx_buf[13] = {0};
    tx_buf[0] = 0x80 | 0x22;

    platform_spi_cs_low();
    bool status = platform_spi_transfer(tx_buf, rx_buf, sizeof(tx_buf));
    platform_spi_cs_high();

    if (!status) {
        return false;
    }

    /* Байт rx_buf[0] - порожній під час передачі адреси, виміри в rx_buf[1..12] */
    const uint8_t *d = &rx_buf[1];
    out_data->gyro[0]  = (int16_t)((uint16_t)d[0]  | ((uint16_t)d[1]  << 8));
    out_data->gyro[1]  = (int16_t)((uint16_t)d[2]  | ((uint16_t)d[3]  << 8));
    out_data->gyro[2]  = (int16_t)((uint16_t)d[4]  | ((uint16_t)d[5]  << 8));
    out_data->accel[0] = (int16_t)((uint16_t)d[6]  | ((uint16_t)d[7]  << 8));
    out_data->accel[1] = (int16_t)((uint16_t)d[8]  | ((uint16_t)d[9]  << 8));
    out_data->accel[2] = (int16_t)((uint16_t)d[10] | ((uint16_t)d[11] << 8));

    return true;
}
