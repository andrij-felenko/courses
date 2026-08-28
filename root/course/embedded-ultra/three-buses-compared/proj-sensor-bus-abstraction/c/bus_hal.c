/* ============================================================================
 * bus_hal.h & bus_hal.c — Уніфікований шар шин автопілота на C
 * ============================================================================ */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Коди результатів операцій на шині */
typedef enum {
    BUS_OK = 0,
    BUS_ERR_TIMEOUT,
    BUS_ERR_NACK,
    BUS_ERR_ARBITRATION_LOST,
    BUS_ERR_INVALID_PARAM,
    BUS_ERR_BUSY
} bus_status_t;

/* Опереджувальне оголошення дескриптора пристрою */
typedef struct bus_device bus_device_t;

/* Таблиця віртуальних методів операцій шини */
typedef struct {
    bus_status_t (*write_reg)(const bus_device_t *dev, uint8_t reg, const uint8_t *data, size_t len);
    bus_status_t (*read_reg)(const bus_device_t *dev, uint8_t reg, uint8_t *data, size_t len);
    bus_status_t (*transfer)(const bus_device_t *dev, const uint8_t *tx, uint8_t *rx, size_t len);
} bus_ops_t;

/* Загальний дескриптор пристрою на шині */
struct bus_device {
    const bus_ops_t *ops;
    void *bus_handle;       /* Вказівник на апаратний дескриптор (SPI_TypeDef, I2C_TypeDef) */
    uint32_t config_param;  /* Номер ніжки CS для SPI або 7-бітна адреса для I2C */
};

/* ----------------------------------------------------------------------------
 * Реалізація адаптера SPI
 * ---------------------------------------------------------------------------- */
extern void gpio_pin_write(uint32_t pin, bool level);
extern bus_status_t spi_hardware_transfer(void *spi_inst, const uint8_t *tx, uint8_t *rx, size_t len);

static bus_status_t spi_dev_write_reg(const bus_device_t *dev, uint8_t reg, const uint8_t *data, size_t len) {
    uint32_t cs_pin = dev->config_param;
    uint8_t reg_header = reg & 0x7F; /* Біт 7 = 0 для запису в типових SPI-сенсорах */

    gpio_pin_write(cs_pin, false); /* Активуємо Chip Select (Active LOW) */
    
    bus_status_t status = spi_hardware_transfer(dev->bus_handle, &reg_header, NULL, 1);
    if (status == BUS_OK && len > 0 && data != NULL) {
        status = spi_hardware_transfer(dev->bus_handle, data, NULL, len);
    }
    
    gpio_pin_write(cs_pin, true); /* Деактивуємо Chip Select */
    return status;
}

static bus_status_t spi_dev_read_reg(const bus_device_t *dev, uint8_t reg, uint8_t *data, size_t len) {
    uint32_t cs_pin = dev->config_param;
    uint8_t reg_header = reg | 0x80; /* Біт 7 = 1 для читання */

    gpio_pin_write(cs_pin, false);
    
    bus_status_t status = spi_hardware_transfer(dev->bus_handle, &reg_header, NULL, 1);
    if (status == BUS_OK && len > 0 && data != NULL) {
        status = spi_hardware_transfer(dev->bus_handle, NULL, data, len);
    }
    
    gpio_pin_write(cs_pin, true);
    return status;
}

static bus_status_t spi_dev_transfer(const bus_device_t *dev, const uint8_t *tx, uint8_t *rx, size_t len) {
    uint32_t cs_pin = dev->config_param;
    gpio_pin_write(cs_pin, false);
    bus_status_t status = spi_hardware_transfer(dev->bus_handle, tx, rx, len);
    gpio_pin_write(cs_pin, true);
    return status;
}

static const bus_ops_t g_spi_bus_ops = {
    .write_reg = spi_dev_write_reg,
    .read_reg  = spi_dev_read_reg,
    .transfer  = spi_dev_transfer
};

void spi_device_init(bus_device_t *dev, void *spi_inst, uint32_t cs_pin) {
    dev->ops = &g_spi_bus_ops;
    dev->bus_handle = spi_inst;
    dev->config_param = cs_pin;
    gpio_pin_write(cs_pin, true);
}

/* ----------------------------------------------------------------------------
 * Реалізація адаптера I2C з процедурою відновлення шини (Bus Recovery)
 * ---------------------------------------------------------------------------- */
extern bus_status_t i2c_hardware_write(void *i2c_inst, uint8_t addr, uint8_t reg, const uint8_t *data, size_t len);
extern bus_status_t i2c_hardware_read(void *i2c_inst, uint8_t addr, uint8_t reg, uint8_t *data, size_t len);
extern void i2c_gpio_mode_set_gpio(void);
extern void i2c_gpio_mode_set_hardware(void);
extern bool i2c_gpio_read_sda(void);
extern void i2c_gpio_write_scl(bool level);
extern void i2c_gpio_write_sda(bool level);
extern void delay_us(uint32_t us);

/* Апаратне відновлення шини I2C при зависанні веденого пристрою в стані LOW */
void i2c_bus_recover(void) {
    i2c_gpio_mode_set_gpio();
    i2c_gpio_write_sda(true);
    i2c_gpio_write_scl(true);
    delay_us(5);

    /* Якщо лінія SDA притиснута до землі, генеруємо до 9 імпульсів SCL */
    for (int i = 0; i < 9; i++) {
        if (i2c_gpio_read_sda()) {
            break; /* Ведений пристрій відпустив лінію SDA */
        }
        i2c_gpio_write_scl(false);
        delay_us(5);
        i2c_gpio_write_scl(true);
        delay_us(5);
    }

    /* Формуємо примусову умову STOP: перехід SDA з LOW у HIGH при високому SCL */
    i2c_gpio_write_sda(false);
    delay_us(5);
    i2c_gpio_write_scl(true);
    delay_us(5);
    i2c_gpio_write_sda(true);
    delay_us(5);

    i2c_gpio_mode_set_hardware();
}

static bus_status_t i2c_dev_write_reg(const bus_device_t *dev, uint8_t reg, const uint8_t *data, size_t len) {
    uint8_t addr = (uint8_t)dev->config_param;
    bus_status_t status = i2c_hardware_write(dev->bus_handle, addr, reg, data, len);
    if (status == BUS_ERR_TIMEOUT) {
        i2c_bus_recover();
    }
    return status;
}

static bus_status_t i2c_dev_read_reg(const bus_device_t *dev, uint8_t reg, uint8_t *data, size_t len) {
    uint8_t addr = (uint8_t)dev->config_param;
    bus_status_t status = i2c_hardware_read(dev->bus_handle, addr, reg, data, len);
    if (status == BUS_ERR_TIMEOUT) {
        i2c_bus_recover();
    }
    return status;
}

static const bus_ops_t g_i2c_bus_ops = {
    .write_reg = i2c_dev_write_reg,
    .read_reg  = i2c_dev_read_reg,
    .transfer  = NULL /* I2C за своєю природою напівдуплексний */
};

void i2c_device_init(bus_device_t *dev, void *i2c_inst, uint8_t i2c_7bit_addr) {
    dev->ops = &g_i2c_bus_ops;
    dev->bus_handle = i2c_inst;
    dev->config_param = (uint32_t)i2c_7bit_addr;
}

/* ----------------------------------------------------------------------------
 * Драйвер IMU (ICM-42688-P) над уніфікованою шиною
 * ---------------------------------------------------------------------------- */
typedef struct {
    int16_t accel_x, accel_y, accel_z;
    int16_t gyro_x,  gyro_y,  gyro_z;
    int16_t temp;
} imu_raw_t;

bus_status_t icm42688_read_raw(const bus_device_t *dev, imu_raw_t *out) {
    uint8_t raw_buf[14];
    /* Адреса початкового регістра даних акселерометра ICM42688_REG_ACCEL_DATA_X1 = 0x1F */
    bus_status_t status = dev->ops->read_reg(dev, 0x1F, raw_buf, sizeof(raw_buf));
    if (status != BUS_OK) {
        return status;
    }

    out->accel_x = (int16_t)((raw_buf[0]  << 8) | raw_buf[1]);
    out->accel_y = (int16_t)((raw_buf[2]  << 8) | raw_buf[3]);
    out->accel_z = (int16_t)((raw_buf[4]  << 8) | raw_buf[5]);
    out->gyro_x  = (int16_t)((raw_buf[6]  << 8) | raw_buf[7]);
    out->gyro_y  = (int16_t)((raw_buf[8]  << 8) | raw_buf[9]);
    out->gyro_z  = (int16_t)((raw_buf[10] << 8) | raw_buf[11]);
    out->temp    = (int16_t)((raw_buf[12] << 8) | raw_buf[13]);
    return BUS_OK;
}
