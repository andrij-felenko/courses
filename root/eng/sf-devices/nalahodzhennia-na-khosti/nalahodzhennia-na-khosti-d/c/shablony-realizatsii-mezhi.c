#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* Результати операцій шини */
typedef enum {
    HAL_BUS_OK = 0,
    HAL_BUS_ERR_NACK = -1,
    HAL_BUS_ERR_TIMEOUT = -2,
    HAL_BUS_ERR_OVERRUN = -3
} hal_bus_status_t;

/* Інтерфейс шини: структура з покажчиком на функцію передачі */
typedef struct hal_i2c_interface {
    hal_bus_status_t (*transfer)(struct hal_i2c_interface *self,
                                 uint8_t dev_addr,
                                 const uint8_t *tx_buf, size_t tx_len,
                                 uint8_t *rx_buf, size_t rx_len);
    void *driver_ctx;
} hal_i2c_interface_t;

/* Драйвер периферійного пристрою */
typedef struct {
    hal_i2c_interface_t *bus;
    uint8_t device_address;
    int16_t last_raw_value;
} ambient_sensor_t;

hal_bus_status_t ambient_sensor_read(ambient_sensor_t *dev, int16_t *output) {
    uint8_t reg = 0x02; /* Регістр даних */
    uint8_t raw_data[2] = {0};

    hal_bus_status_t status = dev->bus->transfer(dev->bus, dev->device_address,
                                                 &reg, 1, raw_data, 2);
    if (status != HAL_BUS_OK) {
        return status;
    }

    *output = (int16_t)((raw_data[0] << 8) | raw_data[1]);
    dev->last_raw_value = *output;
    return HAL_BUS_OK;
}
