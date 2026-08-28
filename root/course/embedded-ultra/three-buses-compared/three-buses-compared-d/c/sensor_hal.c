/* ============================================================================
 * sensor_hal.h & sensor_hal.c — Уніфікований інтерфейс шин та драйверів на C
 * ============================================================================ */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef enum {
    BUS_OK = 0,
    BUS_ERROR_TIMEOUT,
    BUS_ERROR_NACK,
    BUS_ERROR_PARAM
} bus_result_t;

typedef struct bus_dev bus_dev_t;

/* Контракт операцій шини */
typedef struct {
    bus_result_t (*read_reg)(const bus_dev_t *dev, uint8_t reg, uint8_t *data, size_t len);
    bus_result_t (*write_reg)(const bus_dev_t *dev, uint8_t reg, const uint8_t *data, size_t len);
} bus_operations_t;

struct bus_dev {
    const bus_operations_t *ops;
    void *hardware_instance; /* SPI_TypeDef* або I2C_TypeDef* */
    uint32_t address_or_pin; /* Номер ніжки CS для SPI або 7-біт адреса I2C */
};

/* --- SPI реалізація операцій шини --- */
extern void hal_gpio_set(uint32_t pin, bool level);
extern bus_result_t hal_spi_transfer(void *inst, const uint8_t *tx, uint8_t *rx, size_t len);

static bus_result_t spi_ops_read_reg(const bus_dev_t *dev, uint8_t reg, uint8_t *data, size_t len) {
    uint32_t cs_pin = dev->address_or_pin;
    uint8_t cmd = reg | 0x80; /* Біт читання для SPI-датчиків */
    
    hal_gpio_set(cs_pin, false); /* CS LOW */
    bus_result_t res = hal_spi_transfer(dev->hardware_instance, &cmd, NULL, 1);
    if (res == BUS_OK && len > 0) {
        res = hal_spi_transfer(dev->hardware_instance, NULL, data, len);
    }
    hal_gpio_set(cs_pin, true);  /* CS HIGH */
    return res;
}

static bus_result_t spi_ops_write_reg(const bus_dev_t *dev, uint8_t reg, const uint8_t *data, size_t len) {
    uint32_t cs_pin = dev->address_or_pin;
    uint8_t cmd = reg & 0x7F; /* Біт запису */
    
    hal_gpio_set(cs_pin, false);
    bus_result_t res = hal_spi_transfer(dev->hardware_instance, &cmd, NULL, 1);
    if (res == BUS_OK && len > 0) {
        res = hal_spi_transfer(dev->hardware_instance, data, NULL, len);
    }
    hal_gpio_set(cs_pin, true);
    return res;
}

static const bus_operations_t g_spi_bus_ops = {
    .read_reg  = spi_ops_read_reg,
    .write_reg = spi_ops_write_reg
};

void bus_dev_init_spi(bus_dev_t *dev, void *spi_inst, uint32_t cs_pin) {
    dev->ops = &g_spi_bus_ops;
    dev->hardware_instance = spi_inst;
    dev->address_or_pin = cs_pin;
    hal_gpio_set(cs_pin, true);
}

/* --- I2C реалізація операцій шини --- */
extern bus_result_t hal_i2c_read(void *inst, uint8_t addr, uint8_t reg, uint8_t *data, size_t len);
extern bus_result_t hal_i2c_write(void *inst, uint8_t addr, uint8_t reg, const uint8_t *data, size_t len);

static bus_result_t i2c_ops_read_reg(const bus_dev_t *dev, uint8_t reg, uint8_t *data, size_t len) {
    uint8_t addr = (uint8_t)dev->address_or_pin;
    return hal_i2c_read(dev->hardware_instance, addr, reg, data, len);
}

static bus_result_t i2c_ops_write_reg(const bus_dev_t *dev, uint8_t reg, const uint8_t *data, size_t len) {
    uint8_t addr = (uint8_t)dev->address_or_pin;
    return hal_i2c_write(dev->hardware_instance, addr, reg, data, len);
}

static const bus_operations_t g_i2c_bus_ops = {
    .read_reg  = i2c_ops_read_reg,
    .write_reg = i2c_ops_write_reg
};

void bus_dev_init_i2c(bus_dev_t *dev, void *i2c_inst, uint8_t addr_7bit) {
    dev->ops = &g_i2c_bus_ops;
    dev->hardware_instance = i2c_inst;
    dev->address_or_pin = (uint32_t)addr_7bit;
}

/* --- Приклад драйвера IMU (ICM-42688-P) через абстрактну шину --- */
typedef struct {
    int16_t accel_x, accel_y, accel_z;
    int16_t gyro_x,  gyro_y,  gyro_z;
} imu_raw_sample_t;

bus_result_t icm42688_get_samples(const bus_dev_t *bus, imu_raw_sample_t *out) {
    uint8_t buf[12];
    /* Зчитуємо 12 байтів починаючи з регістра 0x1F (ACCEL_DATA_X1) */
    bus_result_t res = bus->ops->read_reg(bus, 0x1F, buf, sizeof(buf));
    if (res != BUS_OK) return res;

    out->accel_x = (int16_t)((buf[0] << 8) | buf[1]);
    out->accel_y = (int16_t)((buf[2] << 8) | buf[3]);
    out->accel_z = (int16_t)((buf[4] << 8) | buf[5]);
    out->gyro_x  = (int16_t)((buf[6] << 8) | buf[7]);
    out->gyro_y  = (int16_t)((buf[8] << 8) | buf[9]);
    out->gyro_z  = (int16_t)((buf[10] << 8) | buf[11]);
    return BUS_OK;
}

/* --- Приклад драйвера барометра (MS5611) через абстрактну шину --- */
typedef struct {
    uint32_t raw_pressure;
    uint32_t raw_temperature;
} baro_raw_sample_t;

bus_result_t ms5611_read_adc(const bus_dev_t *bus, uint32_t *raw_val) {
    uint8_t buf[3];
    bus_result_t res = bus->ops->read_reg(bus, 0x00, buf, sizeof(buf));
    if (res != BUS_OK) return res;

    *raw_val = ((uint32_t)buf[0] << 16) | ((uint32_t)buf[1] << 8) | buf[2];
    return BUS_OK;
}
