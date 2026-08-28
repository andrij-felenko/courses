#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Низькорівневий апаратний виклик шини I2C */
extern bool platform_i2c_write_read(uint8_t dev_addr,
                                    const uint8_t *tx_data, size_t tx_len,
                                    uint8_t *rx_data, size_t rx_len);

/* Структура 3-осьового виміру в сирих відліках */
typedef struct {
    int16_t x;
    int16_t y;
    int16_t z;
} raw_axes_t;

/* Пакетне зчитування 6 регістрів виходу акселерометра */
bool lsm6dso_read_accel_raw(uint8_t i2c_addr, raw_axes_t *out_axes) {
    if (out_axes == NULL) {
        return false;
    }

    const uint8_t reg_start = 0x28; /* Адреса OUTX_L_A */
    uint8_t buffer[6];

    /* Виконуємо єдину складену транзакцію: Start -> Write(0x28) -> ReStart -> Read(6B) -> Stop */
    if (!platform_i2c_write_read(i2c_addr, &reg_start, 1, buffer, 6)) {
        return false;
    }

    /* Безпечне Little-Endian розпакування без UB (Type Punning) */
    out_axes->x = (int16_t)((uint16_t)buffer[0] | ((uint16_t)buffer[1] << 8));
    out_axes->y = (int16_t)((uint16_t)buffer[2] | ((uint16_t)buffer[3] << 8));
    out_axes->z = (int16_t)((uint16_t)buffer[4] | ((uint16_t)buffer[5] << 8));

    return true;
}
